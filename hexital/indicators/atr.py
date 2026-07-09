from dataclasses import dataclass, field
from typing import cast

from ..core.indicator import Indicator
from .tr import TR


@dataclass(kw_only=True)
class ATR(Indicator[float | None]):
    """Average True Range - ATR

    Average True Range is used to measure volatility, especially volatility caused by
    gaps or limit moves.

    Sources:
        https://www.tradingview.com/wiki/Average_True_Range_(ATR)

    Output type: `float`

    Args:
        period (int): How many Periods to use. Defaults to 14
    """

    _name: str = field(init=False, default="ATR")
    period: int = 14

    def _initialise(self):
        self.sub_tr = self.add_child(TR())

    def _calculate_reading(self, index: int) -> float | None:
        if self.prev_exists():
            return (
                cast(float, self.prev_reading()) * (self.period - 1)
                + self.sub_tr.reading()
            ) / self.period

        if self.sub_tr.reading_period(self.period, index=index):
            return self.sub_tr.candles_average(self.period, index=index)

        return None
