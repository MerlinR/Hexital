from dataclasses import dataclass

from hexital.types import Indicator


@dataclass(kw_only=True)
class TR(Indicator):
    """True Range

    An method to expand a classical range (high minus low) to include
    possible gap scenarios.

    Sources:
        https://www.macroption.com/true-range/

    """

    indicator_name: str = "TR"

    def _generate_name(self) -> str:
        return f"{self.indicator_name}"

    def _calculate_new_reading(self, index: int = -1) -> float | dict | None:
        high = self.get_reading_by_index(index, "high")
        low = self.get_reading_by_index(index, "low")

        if self.prev_exists(index):
            close = self.get_reading_by_index(index - 1, "close")
            return max(
                high - low,
                abs(high - close),
                abs(low - close),
            )

        return high - low
