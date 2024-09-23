from dataclasses import dataclass, field

from hexital.core.indicator import Indicator
from hexital.indicators.stdev import STDEV


@dataclass(kw_only=True)
class STDEVT(Indicator):
    """Standard Deviation Threshold - STDEVT

    Standard Deviation while calculating threshold returning boolean signal
    if change to input is higher than threshold

    sources:
        ChatGPT

    Output type: `float`

    Args:
        period: How many Periods to use
        input_value: Which input field to calculate the Indicator
        multiplier: A positive float to multiply the Deviation
    """

    _name: str = field(init=False, default="STDEVT")
    period: int = 10
    input_value: str = "close"
    multiplier: float = 2.0

    def _generate_name(self) -> str:
        return f"{self._name}_{self.period}"

    def _initialise(self):
        self.add_sub_indicator(
            STDEV(
                input_value=self.input_value,
                period=self.period,
                fullname_override=f"{self.name}_stdev",
            )
        )

    def _calculate_reading(self, index: int) -> float | dict | None:
        if not self.exists(f"{self.name}_stdev"):
            return False

        return (
            abs(self.reading(self.input_value) - self.prev_reading(self.input_value))
            > self.reading(f"{self.name}_stdev") * self.multiplier
        )
