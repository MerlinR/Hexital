from dataclasses import dataclass, field

from ..analysis.utils import highest, lowest
from ..core.indicator import Indicator, Source


@dataclass(kw_only=True)
class WillR(Indicator[float | None]):
    """William's Percent R - WILLR

    Williams %R is a momentum oscillator that measures the current close
    relative to the highest high and lowest low over a rolling lookback period.

    Output type: `float`

    Args:
        period (int): How many periods to use. Defaults to 14
        source (str): Which input field to compare against the rolling range.
            Defaults to `"close"`
    """

    _name: str = field(init=False, default="WILLR")
    period: int = 14
    source: Source = "close"

    def _generate_name(self) -> str:
        return f"{self._name}_{self.period}"

    def _calculate_reading(self, index: int) -> float | None:
        if not self.reading_period(self.period, "high", index):
            return None

        highest_high = highest(self.candles, "high", self.period, index)
        lowest_low = lowest(self.candles, "low", self.period, index)
        reading = self.src()

        if highest_high is None or lowest_low is None or reading is None:
            return None

        range_ = highest_high - lowest_low
        if range_ == 0:
            return None

        return 100 * ((reading - lowest_low) / range_ - 1)
