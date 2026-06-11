from dataclasses import dataclass, field

from ..core.indicator import Indicator


def true_range(high: float, low: float, prev_close: float) -> float:
    return max(high - low, abs(high - prev_close), abs(low - prev_close))


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
        if index > 0:
            candle = self.candles[index]
            return true_range(
                candle.high, candle.low, self.candles[index - 1].close
            )

        return None
