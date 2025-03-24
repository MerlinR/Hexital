from dataclasses import dataclass, field

from hexital.analysis.utils import highest, lowest
from hexital.core.indicator import Indicator, Source


@dataclass(kw_only=True)
class MOP(Indicator[float | None]):
    """Midpoint Over Period - MOP

    A technical analysis tool that evaluates the average price movement by calculating
    the midpoint between the highest and lowest points over a specified period.
    This indicator aims to provide a smoother representation of price action,
    avoiding the choppiness of extreme highs and lows.

    Sources:
        https://trendspider.com/learning-center/understanding-and-applying-the-midpoint-over-period-indicator-in-trading/

    Output type: `float`

    Args:
        period (int): How many Periods to use. Defaults to 2
        source (str()): Which input field to calculate the Indicator. Defaults to "close"
    """

    _name: str = field(init=False, default="MOP")
    period: int = 2
    source: Source = "close"

    def _generate_name(self) -> str:
        return f"{self._name}_{self.period}"

    def _calculate_reading(self, index: int) -> float | None:
        if self.prev_exists() or self.reading_period(self.period, self.source, index):
            return (
                lowest(self.candles, self.source, self.period, index)
                + highest(self.candles, self.source, self.period, index)
            ) * 0.5
        return None
