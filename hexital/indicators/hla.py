from dataclasses import dataclass, field

from ..core.indicator import Indicator


@dataclass(kw_only=True)
class HLA(Indicator[float]):
    """High Low Average - HLA

    Output type: `float`
    """

    _name: str = field(init=False, default="HLA")

    def _calculate_reading(self, index: int) -> float:
        candle = self.candles[index]
        return (candle.high + candle.low) / 2
