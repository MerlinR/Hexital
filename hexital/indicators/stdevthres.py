from dataclasses import dataclass, field

from hexital.core.indicator import Indicator
from hexital.indicators.stdev import STDEV


@dataclass(kw_only=True)
class STDEVT(Indicator):
    """Standard Deviation Threshold - STDEVT

    Standard Deviation while calculating threshold returning boolean signal
    if change to input is higher than threshold

    Sources:
        ChatGPT

    Output type: `float`

    Args:
        period (int): How many Periods to use. Defaults to 10
        source (str): Which input field to calculate the Indicator. Defaults to "close"
        multiplier (float): A positive float to multiply the Deviation. Defaults to 2.0
    """

    _name: str = field(init=False, default="STDEVT")
    period: int = 10
    source: str = "close"
    multiplier: float = 2.0

    def _generate_name(self) -> str:
        return f"{self._name}_{self.period}"

    def _initialise(self):
        self.add_sub_indicator(
            STDEV(
                source=self.source,
                period=self.period,
                name=f"{self.name}_stdev",
            )
        )

    def _calculate_reading(self, index: int) -> float | dict | None:
        if not self.exists(f"{self.name}_stdev"):
            return False

        return (
            abs(self.reading(self.source) - self.prev_reading(self.source))
            > self.reading(f"{self.name}_stdev") * self.multiplier
        )
