from dataclasses import dataclass, field

from hexital.analysis.movement import highest, lowest
from hexital.core.indicator import Indicator


@dataclass(kw_only=True)
class HighestLowest(Indicator):
    """Highest Lowest

    Simple utility indicator to record and display the highest and lowest values N periods back."""

    _name: str = field(init=False, default="HL")
    period: int = 100

    def _generate_name(self) -> str:
        return f"{self._name}_{self.period}"

    def _calculate_reading(self, index: int) -> float | dict | None:
        return {
            "low": lowest(self.candles, "low", self.period, index),
            "high": highest(self.candles, "high", self.period, index),
        }
