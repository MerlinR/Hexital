from dataclasses import dataclass

from hexital.types import Indicator
from hexital.utilities import utils


@dataclass(kw_only=True)
class SMA(Indicator):
    """Simple Moving Average (SMA)

    The Simple Moving Average is the classic moving average that is the equally
    weighted average over n periods.

    Sources:
        https://www.investopedia.com/terms/s/sma.asp

    Args:
        Input value (str): Default Close
        period (int) Default: 10


    """

    indicator_name: str = "SMA"
    input_value: str = "close"
    period: int = 10

    def _generate_name(self) -> str:
        return f"{self.indicator_name}_{self.period}"

    def _calculate_reading(self, index: int = -1) -> float | dict | None:
        if self.prev_exists():
            return (
                self.prev_reading()
                - (
                    self.reading(self.input_value, index - self.period)
                    - self.reading(self.input_value)
                )
                / self.period
            )

        if self.reading_period(self.period, self.input_value):
            return self.candles_sum(self.period, self.input_value) / self.period

        return None
