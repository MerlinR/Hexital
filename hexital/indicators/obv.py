from dataclasses import dataclass, field

from hexital.core.indicator import Indicator


@dataclass(kw_only=True)
class OBV(Indicator):
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

    def _calculate_reading(self, index: int) -> float | dict | None:
        if self.prev_exists():
            if self.reading("close") == self.prev_reading("close"):
                return self.prev_reading()
            elif self.reading("close") > self.prev_reading("close"):
                return self.prev_reading() + self.reading("volume")

            return self.prev_reading() - self.reading("volume")

        return self.reading("volume")
