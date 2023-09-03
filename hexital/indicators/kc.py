from dataclasses import dataclass
from typing import Optional

from hexital.indicators import ATR, EMA
from hexital.types import Indicator


@dataclass(kw_only=True)
class KC(Indicator):
    """Keltner Channel

    Sources:
        https://www.investopedia.com/terms/k/keltnerchannel.asp

    """

    indicator_name: str = "KC"
    input_value: str = "close"
    period: int = 20
    multiplier: float = 2.0

    def _generate_name(self) -> str:
        return f"{self.indicator_name}_{self.period}_{self.multiplier}"

    def _initialise(self):
        self.add_sub_indicator(
            ATR(
                candles=self.candles,
                period=self.period,
                fullname_override=f"{self.indicator_name}_ATR",
            )
        )

        self.add_sub_indicator(
            EMA(
                candles=self.candles,
                input_value=self.input_value,
                period=self.period,
                fullname_override=f"{self.indicator_name}_EMA",
            )
        )

    def _calculate_reading(self, index: int = -1) -> float | dict | None:
        if not all(
            [
                self.reading(f"{self.indicator_name}_EMA"),
                self.reading(f"{self.indicator_name}_ATR"),
            ]
        ):
            return {"lower": None, "band": None, "upper": None}

        lower = self.reading(f"{self.indicator_name}_EMA") - (
            self.multiplier * self.reading(f"{self.indicator_name}_ATR")
        )

        upper = self.reading(f"{self.indicator_name}_EMA") + (
            self.multiplier * self.reading(f"{self.indicator_name}_ATR")
        )

        return {
            "lower": lower,
            "band": self.reading(f"{self.indicator_name}_EMA"),
            "upper": upper,
        }
