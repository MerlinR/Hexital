from dataclasses import dataclass, field

from hexital.core import Indicator


@dataclass(kw_only=True)
class HighLowAverage(Indicator):
    """Supertrend"""

    _name: str = field(init=False, default="HighLowAverage")

    def _generate_name(self) -> str:
        return f"{self._name}"

    def _calculate_reading(self, index: int) -> float | dict | None:
        return (self.reading("high") + self.reading("low")) / 2
