from dataclasses import dataclass

from hexital.core import Indicator


@dataclass(kw_only=True)
class WMA(Indicator):
    """Weighted Moving Average

    Sources:
        https://www.investopedia.com/ask/answers/071414/whats-difference-between-moving-average-and-weighted-moving-average.asp

    """

    indicator_name: str = "WMA"
    input_value: str = "close"
    period: int = 10

    def _generate_name(self) -> str:
        return f"{self.indicator_name}_{self.period}"

    def _calculate_reading(self, index: int) -> float | dict | None:
        if self.prev_exists() or self.reading_period(self.period, self.input_value):
            values = sum(
                self.reading(self.input_value, i) * (self.period - py)
                for py, i in enumerate(range(index, index - self.period, -1))
            )
            weight = (self.period * (self.period + 1)) / 2
            return values / weight
        return None
