from dataclasses import dataclass, field

from hexital.core.indicator import Indicator


@dataclass(kw_only=True)
class TR(Indicator):
    """True Range - TR

    An method to expand a classical range (high minus low) to include
    possible gap scenarios.

    Sources:
        https://www.macroption.com/true-range/

    Output type: `float`
    """

    _name: str = field(init=False, default="TR")

    def _generate_name(self) -> str:
        return self._name

    def _calculate_reading(self, index: int) -> float | dict | None:
        if self.prev_exists("close"):
            close = self.candles[index - 1].close
            high = self.candles[index].high
            low = self.candles[index].low
            return max(high - low, abs(high - close), abs(low - close))

        return None
