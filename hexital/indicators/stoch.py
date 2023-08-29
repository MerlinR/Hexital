from dataclasses import dataclass

from hexital.indicators import SMA
from hexital.types import Indicator


@dataclass()
class STOCH(Indicator):
    """Stochastic (STOCH)

    The Stochastic Oscillator (STOCH) was developed by George Lane in the 1950's.
    He believed this indicator was a good way to measure momentum because changes in
    momentum precede changes in price.

    It is a range-bound oscillator with two lines moving between 0 and 100.
    The first line (%K) displays the current close in relation to the period's
    high/low range. The second line (%D) is a Simple Moving Average of the %K line.
    The most common choices are a 14 period %K and a 3 period SMA for %D.

    Sources:
        https://www.tradingview.com/wiki/Stochastic_(STOCH)

    Args:
        period (int) Default: 14
        smoothing (int) Default: 3
        k (int) Default: 14
        d (int) Default: 3

    """

    indicator_name: str = "STOCH"
    period: int = 14
    k: int = 14
    d: int = 3

    def _generate_name(self) -> str:
        return f"{self.indicator_name}_{self.period}"

    def _initialise(self):
        self.add_sub_indicator(
            SMA(
                candles=self.candles,
                fullname_override=f"{self.indicator_name}_EMA_smooth",
                period=self.fast_period,
            )
        )

    def _calculate_reading(self, index: int = -1) -> float | dict | None:
        return None
