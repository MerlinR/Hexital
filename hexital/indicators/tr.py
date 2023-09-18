from dataclasses import dataclass

from hexital.core import Indicator


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
        return self.indicator_name

    def _calculate_reading(self, index: int) -> float | dict | None:
        high = self.reading("high")
        low = self.reading("low")

        if index > 0:
            close = self.prev_reading("close")
            return max(
                high - low,
                abs(high - close),
                abs(low - close),
            )

        return None
