from dataclasses import dataclass, field
from typing import Optional

from hexital.core.indicator import Indicator, Managed
from hexital.indicators.atr import ATR
from hexital.indicators.rma import RMA


@dataclass(kw_only=True)
class ADX(Indicator):
    """Average Directional Index - ADX

    ADX is a trend strength in a series of prices of a financial instrument.

    Sources:
        https://en.wikipedia.org/wiki/Average_directional_movement_index

    Output type: `Dict["ADX": float, "DM_Plus": float, "DM_Neg": float]`

    Args:
        period (int): How many Periods to use. Defaults to 14
        period_signal (Optional[int]):  Average Directional Index period. Defaults same as period
        multiplier (Optional[float]): ADX smoothing multiplier. Defaults to 100.0
    """

    _name: str = field(init=False, default="ADX")

    period: int = 14
    period_signal: Optional[int] = None
    multiplier: float = 100.0

    def _generate_name(self) -> str:
        return f"{self._name}_{self.period}_{self.period_signal}"

    def _validate_fields(self):
        if self.period_signal is None:
            self.period_signal = self.period

    def _initialise(self):
        self.sub_atr = self.add_sub_indicator(
            ATR(
                period=self.period,
            )
        )

        self.data = self.add_managed_indicator("data", Managed(name=f"{self.name}_data"))

        self.sub_pos = self.data.add_sub_indicator(
            RMA(
                name=f"{self.name}_positive",
                period=self.period,
                source=f"{self.data.name}.positive",
            ),
            False,
        )
        self.sub_neg = self.data.add_sub_indicator(
            RMA(
                name=f"{self.name}_negative",
                period=self.period,
                source=f"{self.data.name}.negative",
            ),
            False,
        )
        self.dx = self.add_managed_indicator(
            "dx",
            RMA(
                name=f"{self.name}_dx",
                period=self.period_signal,
                source=f"{self.data.name}.dx",
            ),
        )

    def _calculate_reading(self, index: int) -> float | dict | None:
        adx_positive = None
        adx_negative = None

        if self.prev_exists("high"):
            up = self.candles[index].high - self.candles[index - 1].high
            down = self.candles[index - 1].low - self.candles[index].low
        else:
            up = 0
            down = 0

        dm_plus = ((up > down) & (up > 0)) * up
        dm_neg = ((down > up) & (down > 0)) * down

        self.data.set_reading({"positive": dm_plus, "negative": dm_neg})

        atr_ = self.sub_atr.reading()

        if self.sub_pos.exists() and atr_ is not None:
            mod = self.multiplier / atr_

            adx_positive = mod * self.sub_pos.reading()
            adx_negative = mod * self.sub_neg.reading()

            dx = self.multiplier * abs(adx_positive - adx_negative) / (adx_positive + adx_negative)

            self.data.set_reading({"positive": dm_plus, "negative": dm_neg, "dx": dx})
            self.dx.calculate_index(index)

        return {
            "ADX": self.dx.reading(),
            "DM_Plus": adx_positive,
            "DM_Neg": adx_negative,
        }
