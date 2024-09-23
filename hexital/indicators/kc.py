from dataclasses import dataclass, field

from hexital.core.indicator import Indicator
from hexital.indicators import ATR, EMA


@dataclass(kw_only=True)
class KC(Indicator):
    """Keltner Channel - KC

    Keltner channel is a technical analysis indicator showing a central moving
    average line plus channel lines at a distance above and below.
    A popular volatility indicator similar to Bollinger Bands and Donchian Channels.

    Sources:
        https://www.investopedia.com/terms/k/keltnerchannel.asp

    Output type: `Dict["lower": float, "band": float, "upper": float]`

    Args:
        period: How many Periods to use
        input_value: Which input field to calculate the Indicator
        multiplier: A positive float to multiply the bands
    """

    _name: str = field(init=False, default="KC")
    period: int = 20
    input_value: str = "close"
    multiplier: float = 2.0

    def _generate_name(self) -> str:
        return f"{self._name}_{self.period}_{self.multiplier}"

    def _initialise(self):
        self.add_sub_indicator(
            ATR(
                period=self.period,
                fullname_override=f"{self.name}_ATR",
            )
        )

        self.add_sub_indicator(
            EMA(
                input_value=self.input_value,
                period=self.period,
                fullname_override=f"{self.name}_EMA",
            )
        )

    def _calculate_reading(self, index: int) -> float | dict | None:
        atr_ = self.reading(f"{self.name}_ATR")

        if atr_ is None:
            return {"lower": None, "band": self.reading(f"{self.name}_EMA"), "upper": None}

        lower = self.reading(f"{self.name}_EMA") - (self.multiplier * atr_)
        upper = self.reading(f"{self.name}_EMA") + (self.multiplier * atr_)

        return {
            "lower": lower,
            "band": self.reading(f"{self.name}_EMA"),
            "upper": upper,
        }
