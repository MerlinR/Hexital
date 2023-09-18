from dataclasses import dataclass

from hexital.core import Indicator
from hexital.indicators.tr import TR
from hexital.lib import utils


@dataclass(kw_only=True)
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

    def _generate_name(self) -> str:
        return f"{self.indicator_name}_{self.period}"

    def _initialise(self):
        self._add_sub_indicator(TR(candles=self.candles))

    def _calculate_reading(self, index: int) -> float | dict | None:
        if self.prev_exists():
            return (
                self.prev_reading() * (self.period - 1) + self.reading("TR")
            ) / self.period

        if self.reading_period(self.period, "TR"):
            return self.candles_sum(self.period, "TR") / self.period
        return None
