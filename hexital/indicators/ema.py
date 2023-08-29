from dataclasses import dataclass

from hexital.types import Indicator
from hexital.utilities import utils


@dataclass(kw_only=True)
class EMA(Indicator):
    """Exponential Moving Average (EMA)

    The Exponential Moving Average is more responsive moving average compared to the
    Simple Moving Average (SMA).  The weights are determined by alpha which is
    proportional to it's length.

    Sources:
        https://www.investopedia.com/ask/answers/122314/what-exponential-moving-average-ema-formula-and-how-ema-calculated.asp

    Args:
        Input value (str): Default Close
        period (int) Default: 10

    """

    indicator_name: str = "EMA"
    input_value: str = "close"
    period: int = 10
    smoothing: float = 2.0

    _min_period: int = 10

    def _generate_name(self) -> str:
        return f"{self.indicator_name}_{self.period}"

    def _initialise(self):
        self.period = self.period if self.period > 10 else self._min_period

    def _calculate_reading(self, index: int = -1) -> float | dict | None:
        if self.prev_exists(index):
            multiplier = float(self.smoothing / (self.period + 1.0))
            return float(
                multiplier * self.reading_by_index(index, self.input_value)
                + (self.reading_by_index(index - 1) * (1.0 - multiplier))
            )

        if self.reading_period(self.period, index=index, name=self.input_value):
            return float(
                utils.candles_sum(
                    self.candles, self.input_value, length=self.period, index=index
                )
                / self.period
            )

        return None
