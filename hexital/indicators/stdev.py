from dataclasses import dataclass, field
from math import sqrt

from hexital.core.indicator import Indicator, Managed


@dataclass(kw_only=True)
class STDEV(Indicator):
    """Rolling Standard Deviation - STDEV

    You use a rolling stdev when you expect the standard deviation to change over time.
    As long as the standard deviation is changing slowly enough, we should be able to see
    the change in the standard deviation over time if we use the right size window.

    sources:
        https://jonisalonen.com/2014/efficient-and-accurate-rolling-standard-deviation/

    Output type: `float`

    Args:
        period: How many Periods to use
        input_value: Which input field to calculate the Indicator
    """

    _name: str = field(init=False, default="STDEV")
    period: int = 30
    input_value: str = "close"

    def _generate_name(self) -> str:
        return f"{self._name}_{self.period}"

    def _initialise(self):
        self.add_managed_indicator("data", Managed(fullname_override=f"{self.name}_data"))

    def _calculate_reading(self, index: int) -> float | dict | None:
        popped_reading = 0

        reading = self.reading(self.input_value)

        if reading is None:
            return None

        if self.reading_period(self.period + 1, self.input_value, index):
            popped_reading = self.reading(self.input_value, index - self.period)

        old_mean = self.prev_reading(f"{self.name}_data.mean", 0.0)
        variance = self.prev_reading(f"{self.name}_data.variance", 0.0)

        mean_ = old_mean + (reading - popped_reading) / self.period

        variance += (
            (reading - popped_reading)
            * (reading - mean_ + popped_reading - old_mean)
            / (self.period)
        )

        self.managed_indicators["data"].set_reading({"mean": mean_, "variance": variance})

        if self.prev_exists() or self.reading_period(self.period, self.input_value, index):
            return sqrt(variance) if variance > 0 else 0
