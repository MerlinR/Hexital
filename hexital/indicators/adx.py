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
        self.add_sub_indicator(
            ATR(
                period=self.period,
                name=f"{self.name}_atr",
            )
        )
        data_indicator = Managed(name=f"{self.name}_data")
        self.add_managed_indicator("data", data_indicator)

        data_indicator.add_sub_indicator(
            RMA(
                name=f"{self.name}_positive",
                period=self.period,
                source=f"{self.name}_data.positive",
            ),
            False,
        )
        data_indicator.add_sub_indicator(
            RMA(
                name=f"{self.name}_negative",
                period=self.period,
                source=f"{self.name}_data.negative",
            ),
            False,
        )
        self.add_managed_indicator(
            "dx",
            RMA(
                name=f"{self.name}_dx",
                period=self.period_signal,
                source=f"{self.name}_data.dx",
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

        self.managed_indicators["data"].set_reading({"positive": dm_plus, "negative": dm_neg})

        atr_ = self.reading(f"{self.name}_atr")

        if self.exists(f"{self.name}_positive") and atr_ is not None:
            mod = self.multiplier / atr_

            adx_positive = mod * self.reading(f"{self.name}_positive")
            adx_negative = mod * self.reading(f"{self.name}_negative")

            dx = self.multiplier * abs(adx_positive - adx_negative) / (adx_positive + adx_negative)

            self.managed_indicators["data"].set_reading(
                {"positive": dm_plus, "negative": dm_neg, "dx": dx}
            )
            self.managed_indicators["dx"].calculate_index(index)

        return {
            "ADX": self.reading(f"{self.name}_dx"),
            "DM_Plus": adx_positive,
            "DM_Neg": adx_negative,
        }
