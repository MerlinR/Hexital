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
        period: How many Periods to use
        period_signal:  Average Directional Index period, defaults same as period
        multiplier: ADX smoothing multiplier
    """

    _name: str = field(init=False, default="ADX")

    period: int = 14
    period_signal: Optional[int] = None
    multiplier: int = 100

    def _generate_name(self) -> str:
        return f"{self._name}_{self.period}_{self.period_signal}"

    def _validate_fields(self):
        if self.period_signal is None:
            self.period_signal = self.period

    def _initialise(self):
        self.add_sub_indicator(
            ATR(
                period=self.period,
                fullname_override=f"{self.name}_atr",
            )
        )
        data_indicator = Managed(fullname_override=f"{self.name}_data")
        self.add_managed_indicator("data", data_indicator)

        data_indicator.add_sub_indicator(
            RMA(
                fullname_override=f"{self.name}_positive",
                period=self.period,
                input_value=f"{self.name}_data.positive",
            ),
            False,
        )
        data_indicator.add_sub_indicator(
            RMA(
                fullname_override=f"{self.name}_negative",
                period=self.period,
                input_value=f"{self.name}_data.negative",
            ),
            False,
        )
        self.add_managed_indicator(
            "dx",
            RMA(
                fullname_override=f"{self.name}_dx",
                period=self.period_signal,
                input_value=f"{self.name}_data.dx",
            ),
        )

    def _calculate_reading(self, index: int) -> float | dict | None:
        adx_final = None
        adx_positive = None
        adx_negative = None

        if self.prev_exists("high"):
            up = self.candles[index].high - self.candles[index - 1].high
            down = self.candles[index - 1].low - self.candles[index].low
        else:
            up = self.candles[index].high - self.candles[index].low
            down = 0

        dm_plus = up if up > down and up > 0.0 else 0.0
        dm_neg = down if down > up and down > 0.0 else 0.0

        self.managed_indicators["data"].set_reading({"positive": dm_plus, "negative": dm_neg})

        if self.exists(f"{self.name}_atr"):
            mod = self.multiplier / self.reading(f"{self.name}_atr")

            adx_positive = mod * self.reading(f"{self.name}_positive")
            adx_negative = mod * self.reading(f"{self.name}_negative")

            dx = self.multiplier * abs(adx_positive - adx_negative) / (adx_positive + adx_negative)

            self.managed_indicators["data"].set_reading(
                {"positive": dm_plus, "negative": dm_neg, "dx": dx}
            )
            self.managed_indicators["dx"].calculate_index(index)

            adx_final = self.reading(f"{self.name}_dx")

        return {"ADX": adx_final, "DM_Plus": adx_positive, "DM_Neg": adx_negative}
