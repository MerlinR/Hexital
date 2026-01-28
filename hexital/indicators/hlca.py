from dataclasses import dataclass, field

from ..core.indicator import Indicator


@dataclass(kw_only=True)
class HLCA(Indicator[float]):
    """High Low Close Average - HLCA

    Output type: `float`
    """

    _name: str = field(init=False, default="HLCA")

    def _calculate_reading(self, index: int) -> float:
        candle = self.candles[index]
        return (candle.high + candle.low + candle.close) / 3
