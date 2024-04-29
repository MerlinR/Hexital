from dataclasses import dataclass, field

from hexital.core.indicator import Indicator
from hexital.indicators.stdev import StandardDeviation


@dataclass(kw_only=True)
class StandardDeviationThreshold(Indicator):
    """Standard Deviation Threshold

    Standard Deviation while calculating threshold returning boolean signal
    if change to input is higher than threshold
    """

    _name: str = field(init=False, default="STDEVTHRES")
    period: int = 10
    multiplier: float = 2.0
    input_value: str = "close"

    def _generate_name(self) -> str:
        return f"{self._name}_{self.period}"

    def _initialise(self):
        self.add_sub_indicator(
            StandardDeviation(
                input_value=self.input_value,
                period=self.period,
                fullname_override=f"{self.name}_stdev",
            )
        )

    def _calculate_reading(self, index: int) -> float | dict | None:
        if self.reading(f"{self.name}_stdev") is None:
            return False

        return (
            abs(self.reading(self.input_value) - self.prev_reading(self.input_value))
            > self.reading(f"{self.name}_stdev") * self.multiplier
        )
