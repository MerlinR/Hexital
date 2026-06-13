from dataclasses import dataclass, field

from ..core.indicator import Indicator, Source
from .sma import SMA
from .stdev import STDEV


@dataclass(kw_only=True)
class ZScore(Indicator[float | None]):
    """Rolling Z Score - ZS

    The rolling z-score measures how far the current value is from its rolling
    mean in units of rolling standard deviation. It is commonly used to detect
    statistical extremes and mean-reversion conditions.

    Output type: `float`

    Args:
        period (int): How many periods to use. Defaults to 30
        source (str): Which input field to calculate the indicator from.
            Defaults to `"close"`
        std (float): Standard deviation multiplier applied to the denominator.
            Defaults to 1.0
    """

    _name: str = field(init=False, default="ZS")
    period: int = 30
    source: Source = "close"
    std: float = 1.0

    def _generate_name(self) -> str:
        return f"{self._name}_{self.period}"

    def _initialise(self):
        self.sub_sma = self.add_child(SMA(source=self.source, period=self.period))
        self.sub_stdev = self.add_child(STDEV(source=self.source, period=self.period))

    def _calculate_reading(self, index: int) -> float | None:
        mean_ = self.sub_sma.reading()
        stdev_ = self.sub_stdev.reading()
        reading = self.src()

        if mean_ is None or stdev_ is None or reading is None:
            return None

        scaled_stdev = self.std * stdev_
        if scaled_stdev == 0:
            return None

        return (reading - mean_) / scaled_stdev
