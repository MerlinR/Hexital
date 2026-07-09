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

    def _calculate_reading(self, index: int) -> float | None:
        if index > 0:
            candle = self.candles[index]

            return max(
                candle.high - candle.low,
                abs(candle.high - self.candles[index - 1].close),
                abs(candle.low - self.candles[index - 1].close),
            )

        return None
