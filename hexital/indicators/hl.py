from dataclasses import dataclass

from hexital.core import Indicator


@dataclass(kw_only=True)
class HighLowAverage(Indicator):
    """Supertrend"""

    indicator_name: str = "HighLowAverage"

    def _generate_name(self) -> str:
        return f"{self.indicator_name}"

    def _calculate_reading(self, index: int) -> float | dict | None:
        return (self.reading("high") + self.reading("low")) / 2
