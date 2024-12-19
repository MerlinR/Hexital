from dataclasses import dataclass, field

from hexital.core.indicator import Indicator
from hexital.indicators.tr import TR


@dataclass(kw_only=True)
class ATR(Indicator):
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

    def _generate_name(self) -> str:
        return f"{self._name}_{self.period}"

    def _initialise(self):
        self.add_sub_indicator(TR())

    def _calculate_reading(self, index: int) -> float | dict | None:
        if self.prev_exists():
            return (self.prev_reading() * (self.period - 1) + self.reading("TR")) / self.period

        if self.reading_period(self.period, "TR"):
            return self.candles_average(self.period, "TR")

        return None
