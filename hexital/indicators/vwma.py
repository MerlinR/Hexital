from dataclasses import dataclass, field
from typing import cast

from ..core.indicator import Indicator


@dataclass(kw_only=True)
class VWMA(Indicator[float | None]):
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

    def _initialise(self):
        self._state = self.add_state()

    def _calculate_reading(self, index: int) -> float | None:
        price_volume = self.close * self.volume

        if self.prev_exists():
            old_candle = self.candles[index - self.period]
            price_volume_sum = self._state.prev("price_volume_sum")
            volume_sum = self._state.prev("volume_sum")

            if price_volume_sum is None or volume_sum is None:
                return None

            price_volume_sum = price_volume_sum - (old_candle.close * old_candle.volume) + price_volume
            volume_sum = volume_sum - old_candle.volume + self.volume

            self._state.set(
                {
                    "price_volume_sum": price_volume_sum,
                    "volume_sum": volume_sum,
                }
            )

            if volume_sum == 0:
                return None

            return price_volume_sum / volume_sum

        if self.reading_period(self.period, "close"):
            candles = self.candles[index - self.period + 1 : index + 1]
            price_volume_sum = sum(candle.close * candle.volume for candle in candles)
            volume_sum = sum(cast(int, candle.volume) for candle in candles)

            self._state.set(
                {
                    "price_volume_sum": price_volume_sum,
                    "volume_sum": volume_sum,
                }
            )

            if volume_sum == 0:
                return None

            return price_volume_sum / volume_sum

        return None
