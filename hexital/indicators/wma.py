from dataclasses import dataclass, field
from typing import cast

from ..core.indicator import Indicator, Source


@dataclass(kw_only=True)
class WMA(Indicator[float | None]):
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
    source: Source = "close"
    _denom: float = field(init=False, default=0)

    def _generate_name(self) -> str:
        return f"{self._name}_{self.period}"

    def _validate_fields(self):
        self._denom = (self.period * (self.period + 1)) / 2

    def _initialise(self):
        self._state = self.add_state()

    def _calculate_reading(self, index: int) -> float | None:
        reading = self.src()
        if reading is None:
            return None

        if self.prev_exists():
            prev = self.prev_reading()
            oldest = self.at_src(index - self.period)
            window_sum = self._state.prev("window_sum")
            if prev is None or oldest is None or window_sum is None:
                return None

            new_num = (prev * self._denom) - window_sum + (self.period * reading)
            self._state.update(window_sum=window_sum - oldest + reading)
            return new_num / self._denom

        if self.reading_period(self.period, self.source):
            values = [
                cast(float, self.at_src(i))
                for i in range(index - self.period + 1, index + 1)
            ]
            window_sum = sum(values)
            num = sum((py + 1) * val for py, val in enumerate(values))
            self._state.update(window_sum=window_sum)
            return num / self._denom

        return None
