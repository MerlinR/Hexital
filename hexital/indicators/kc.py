from dataclasses import dataclass, field

from hexital.core.indicator import Indicator
from hexital.indicators import ATR, EMA


@dataclass(kw_only=True)
class KC(Indicator):
    """Keltner Channel

    Sources:
        https://www.investopedia.com/terms/k/keltnerchannel.asp

    """

    _name: str = field(init=False, default="KC")
    period: int = 20
    multiplier: float = 2.0
    input_value: str = "close"

    def _generate_name(self) -> str:
        return f"{self._name}_{self.period}_{self.multiplier}"

    def _initialise(self):
        self._add_sub_indicator(
            ATR(
                period=self.period,
                fullname_override=f"{self._name}_ATR",
            )
        )

        self._add_sub_indicator(
            EMA(
                input_value=self.input_value,
                period=self.period,
                fullname_override=f"{self._name}_EMA",
            )
        )

    def _calculate_reading(self, index: int) -> float | dict | None:
        if not all(
            [
                self.reading(f"{self._name}_EMA"),
                self.reading(f"{self._name}_ATR"),
            ]
        ):
            return {"lower": None, "band": None, "upper": None}

        lower = self.reading(f"{self._name}_EMA") - (
            self.multiplier * self.reading(f"{self._name}_ATR")
        )

        upper = self.reading(f"{self._name}_EMA") + (
            self.multiplier * self.reading(f"{self._name}_ATR")
        )

        return {
            "lower": lower,
            "band": self.reading(f"{self._name}_EMA"),
            "upper": upper,
        }
