from dataclasses import dataclass, field

from ..core.indicator import Indicator


@dataclass(kw_only=True)
class OBV(Indicator[float]):
    """On-Balance Volume - OBC

    On-balance volume (OBV) is a technical analysis indicator intended
    to relate price and volume in the stock market.
    OBV is based on a cumulative total volume.

    Sources:
       https://en.wikipedia.org/wiki/On-balance_volume

    Output type: `float`
    """

    _name: str = field(init=False, default="OBV")

    def _calculate_reading(self, index: int) -> float:
        candle = self.candles[index]

        if self.prev_exists():
            if candle.close == self.candles[index - 1].close:
                return self.prev_reading()
            if candle.close > self.candles[index - 1].close:
                return self.prev_reading() + candle.volume

            return self.prev_reading() - candle.volume

        return candle.volume
