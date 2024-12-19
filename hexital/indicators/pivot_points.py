from dataclasses import dataclass, field

from hexital.core.indicator import Indicator


@dataclass(kw_only=True)
class PivotPoints(Indicator):
    """Pivot Points - PP

    Pivot point is a price level that is used by traders as a possible indicator of market movement.
    A pivot point is calculated as an average of significant prices (high, low, close) from the
    performance of a market in the prior trading period. If the market in the following period trades
    above the pivot point it is 1usually evaluated as a bullish sentiment, whereas trading below
    the pivot point is seen as bearish.

    Sources:
        https://en.wikipedia.org/wiki/Pivot_point_(technical_analysis)

    Output type: `Dict["S1": float, "R1": float, "S2": float, "R2": float]`
    """

    _name: str = field(init=False, default="PP")

    def _generate_name(self) -> str:
        return f"{self._name}"

    def _calculate_reading(self, index: int) -> float | dict | None:
        pivot_points = {"S1": None, "R1": None, "S2": None, "R2": None}

        if self.prev_exists("close"):
            high = self.candles[index - 1].high
            low = self.candles[index - 1].low
            close = self.candles[index - 1].close

            point = (high + low + close) / 3

            pivot_points["S1"] = (point * 2) - high
            pivot_points["R1"] = (point * 2) - low

            pivot_points["S2"] = point - (high - low)
            pivot_points["R2"] = point + (high - low)

        return pivot_points
