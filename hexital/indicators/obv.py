from dataclasses import dataclass, field

from hexital.core.indicator import Indicator


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

    def _generate_name(self) -> str:
        return self._name

    def _calculate_reading(self, index: int) -> float:
        if self.prev_exists():
            if self.candles[index].close == self.candles[index - 1].close:
                return self.prev_reading()
            elif self.candles[index].close > self.candles[index - 1].close:
                return self.prev_reading() + self.candles[index].volume

            return self.prev_reading() - self.candles[index].volume

        return self.candles[index].volume
