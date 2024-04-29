from dataclasses import dataclass, field
from math import sqrt

from hexital.core.indicator import Indicator, Managed


@dataclass(kw_only=True)
class StandardDeviation(Indicator):
    """Rolling Standard Deviation

    https://jonisalonen.com/2014/efficient-and-accurate-rolling-standard-deviation/
    """

    _name: str = field(init=False, default="STDEV")
    period: int = 30
    input_value: str = "close"

    def _generate_name(self) -> str:
        return f"{self._name}_{self.period}"

    def _initialise(self):
        self.add_managed_indicator("STDEV_data", Managed(fullname_override=f"{self.name}_data"))

    def _calculate_reading(self, index: int) -> float | dict | None:
        old_mean = 0
        variance = 0
        removed_val = 0
        in_calc_range = False

        if self.reading(self.input_value) is None:
            return None

        if self.reading_period(self.period + 1, self.input_value, index):
            removed_val = self.reading(self.input_value, index - self.period)
            in_calc_range = True

        if self.prev_exists(f"{self.name}_data.mean"):
            old_mean = self.prev_reading(f"{self.name}_data.mean")

        new_mean = old_mean + (self.reading(self.input_value) - removed_val) / self.period

        if self.prev_exists(f"{self.name}_data.variance"):
            variance = self.prev_reading(f"{self.name}_data.variance")

        variance += (
            (self.reading(self.input_value) - removed_val)
            * (self.reading(self.input_value) - new_mean + removed_val - old_mean)
            / (self.period)
        )

        self.managed_indicators["STDEV_data"].set_reading({"mean": new_mean, "variance": variance})

        if in_calc_range:
            return sqrt(variance)
