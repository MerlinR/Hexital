from dataclasses import dataclass

from hexital.core import Indicator
from hexital.lib.utils import candles_sum


@dataclass(kw_only=True)
class VWMA(Indicator):
    """Volume Weighted Moving Average

    Sources:
        https://www.investopedia.com/ask/answers/071414/whats-difference-between-moving-average-and-weighted-moving-average.asp

    """

    indicator_name: str = "VWMA"
    period: int = 10

    def _generate_name(self) -> str:
        return f"{self.indicator_name}_{self.period}"

    def _calculate_reading(self, index: int) -> float | dict | None:
        if self.prev_exists() or self.reading_period(self.period, "close"):
            volume_close = sum(
                self.reading("close", i) * self.reading("volume", i)
                for i in range(index - (self.period - 1), index + 1)
            )
            return volume_close / candles_sum(self.candles, "volume", self.period, index)
        return None
