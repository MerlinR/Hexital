from dataclasses import dataclass

from hexital.types import Indicator


@dataclass()
class TR(Indicator):
    """True Range

    An method to expand a classical range (high minus low) to include
    possible gap scenarios.

    Sources:
        https://www.macroption.com/true-range/

    """

    indicator_name: str = "TR"

    def _generate_name(self) -> str:
        return self.indicator_name

    def _calculate_reading(self, index: int = -1) -> float | dict | None:
        high = self.reading_by_index(index, "high")
        low = self.reading_by_index(index, "low")

        if index > 0:
            close = self.reading_by_index(index - 1, "close")
            return max(
                high - low,
                abs(high - close),
                abs(low - close),
            )

        return None
