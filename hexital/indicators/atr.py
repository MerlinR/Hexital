from dataclasses import dataclass

from hexital.indicators.tr import TR
from hexital.types import Indicator
from hexital.utilities import utils


@dataclass()
class ATR(Indicator):
    """Average True Range (ATR)

    Averge True Range is used to measure volatility, especially volatility caused by
    gaps or limit moves.

    Sources:
        https://www.tradingview.com/wiki/Average_True_Range_(ATR)

    Args:
        period (int) Default: 14
        percentage (bool) Default: False

    """

    indicator_name: str = "ATR"
    period: int = 14
    percentage: bool = False

    def _generate_name(self) -> str:
        return f"{self.indicator_name}_{self.period}"

    def _initialise(self):
        self.add_sub_indicator(TR(candles=self.candles))

    def _calculate_reading(self, index: int = -1) -> float | dict | None:
        if self.prev_exists(index):
            return (
                self.reading_by_index(index - 1) * (self.period - 1)
                + self.reading_by_index(index, "TR")
            ) / self.period

        if self.reading_period(self.period, index=index, name="TR"):
            return (
                utils.candles_sum(self.candles, "TR", length=self.period, index=index)
                / self.period
            )
        return None
