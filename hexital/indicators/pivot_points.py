from dataclasses import dataclass, field

from hexital.core.indicator import Indicator


@dataclass(kw_only=True)
class PivotPoints(Indicator):
    """Pivot Points (PP)"""

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
