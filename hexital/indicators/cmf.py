from dataclasses import dataclass, field

from ..core.indicator import Indicator
from ..utils.common import non_zero_range


@dataclass(kw_only=True)
class CMF(Indicator[float | None]):
    """Chaikin Money Flow - CMF

    Chaikin Money Flow measures buying and selling pressure by comparing
    rolling money flow volume against rolling total volume.

    Sources:
        https://tradingstrategy.ai/docs/api/technical-analysis/volume/help/pandas_ta.volume.cmf.html

    Output type: `float`

    Args:
        period (int): Rolling window length. Defaults to 20.
    """

    _name: str = field(init=False, default="CMF")
    period: int = 20

    def _initialise(self):
        self._state = self.add_state()

    def _calculate_reading(self, index: int) -> float | None:
        ad = (2 * self.close - (self.high + self.low)) * (
            self.volume / non_zero_range(self.high, self.low)
        )
        self._state.set({"ad": ad, "volume": self.volume})

        if not self.reading_period(self.period, self._state.source("volume"), index):
            return None

        volume_sum = self.candles_sum(self.period, self._state.source("volume"))
        if volume_sum == 0:
            return None

        return self.candles_sum(self.period, self._state.source("ad")) / volume_sum
