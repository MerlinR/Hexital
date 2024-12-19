from dataclasses import dataclass, field

from hexital.core.indicator import Indicator


@dataclass(kw_only=True)
class WMA(Indicator):
    """Weighted Moving Average - WMA

    A Weighted Moving Average puts more weight on recent data and less on past data.
    This is done by multiplying each bar's price by a weighting factor.
    Because of its unique calculation, WMA will follow prices more closely
    than a corresponding Simple Moving Average.

    Sources:
        https://www.investopedia.com/ask/answers/071414/whats-difference-between-moving-average-and-weighted-moving-average.asp

    Output type: `float`

    Args:
        period (int): How many Periods to use. Defaults to 10
        source (str): Which input field to calculate the Indicator. Defaults to "close"
    """

    _name: str = field(init=False, default="WMA")
    period: int = 10
    source: str = "close"

    def _generate_name(self) -> str:
        return f"{self._name}_{self.period}"

    def _calculate_reading(self, index: int) -> float | dict | None:
        if self.prev_exists() or self.reading_period(self.period, self.source):
            values = sum(
                self.reading(self.source, i) * (self.period - py)
                for py, i in enumerate(range(index, index - self.period, -1))
            )
            weight = (self.period * (self.period + 1)) / 2
            return values / weight
        return None
