from dataclasses import dataclass, field
from math import sqrt

from ..core.indicator import Indicator, Source


@dataclass(kw_only=True)
class STDEV(Indicator[float | None]):
    """Rolling Standard Deviation - STDEV

    You use a rolling stdev when you expect the standard deviation to change over time.
    As long as the standard deviation is changing slowly enough, we should be able to see
    the change in the standard deviation over time if we use the right size window.

    Sources:
        https://jonisalonen.com/2014/efficient-and-accurate-rolling-standard-deviation/

    Output type: `float`

    Args:
        period (int): How many Periods to use. Defaults to 30
        source (str): Which input field to calculate the Indicator. Defaults to "close"
    """

    _name: str = field(init=False, default="STDEV")
    period: int = 30
    source: Source = "close"

    def _generate_name(self) -> str:
        return f"{self._name}_{self.period}"

    def _initialise(self):
        self._state = self.add_state()

    def _calculate_reading(self, index: int) -> float | None:
        popped_reading = 0

        reading = self.src()

        if reading is None:
            return None

        if self.reading_period(self.period + 1, self.source, index):
            popped_reading = self.at_src(index - self.period)

        old_mean = self._state.prev("mean", 0.0)
        variance = self._state.prev("variance", 0.0)

        mean_ = old_mean + (reading - popped_reading) / self.period

        variance += (
            (reading - popped_reading)
            * (reading - mean_ + popped_reading - old_mean)
            / (self.period)
        )

        self._state.update(mean=mean_, variance=variance)

        if self.prev_exists() or self.reading_period(self.period, self.source, index):
            return sqrt(variance) if variance > 0 else 0
        return None
