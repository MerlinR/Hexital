from dataclasses import dataclass, field

from hexital.core.indicator import Indicator


@dataclass(kw_only=True)
class VWMA(Indicator):
    """Volume Weighted Moving Average - VWMA

    VWMA is the ratio of the value of a security or financial asset traded to the total
    volume of transactions during a trading session. It is a measure of the average
    trading price for the period.

    Sources:
        https://www.investopedia.com/ask/answers/071414/whats-difference-between-moving-average-and-weighted-moving-average.asp

    Output type: `float`

    Args:
        period (int): How many Periods to use. Defaults to 10
    """

    _name: str = field(init=False, default="VWMA")
    period: int = 10

    def _generate_name(self) -> str:
        return f"{self._name}_{self.period}"

    def _calculate_reading(self, index: int) -> float | dict | None:
        if self.prev_exists() or self.reading_period(self.period, "close"):
            volume_close = sum(
                self.reading("close", i) * self.reading("volume", i)
                for i in range(index - (self.period - 1), index + 1)
            )
            return volume_close / self.candles_sum(self.period, "volume")
        return None
