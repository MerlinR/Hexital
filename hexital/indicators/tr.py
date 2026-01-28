from dataclasses import dataclass, field

from ..core.indicator import Indicator


@dataclass(kw_only=True)
class TR(Indicator[float | None]):
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

    def _calculate_reading(self, index: int) -> float | None:
        candle = self.candles[index]

        if index > 0:
            close = self.candles[index - 1].close
            high = candle.high
            low = candle.low
            return max(high - low, abs(high - close), abs(low - close))

        return None
