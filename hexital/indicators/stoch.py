from dataclasses import dataclass

from hexital.core import Indicator
from hexital.indicators import SMA


@dataclass(kw_only=True)
class STOCH(Indicator):
    """Stochastic (STOCH)

    The Stochastic Oscillator (STOCH) was developed by George Lane in the 1950's.
    He believed this indicator was a good way to measure momentum because changes in
    momentum precede changes in price.

    It is a range-bound oscillator with two lines moving between 0 and 100.
    The first line (%K) displays the current close in relation to the period's
    high/low range. The second line (%D) is a Simple Moving Average of the %K line.
    The most common choices are a 14 period %K and a 3 period SMA for %D.

    %K = SMA(100 * (Current Close - Lowest Low) / (Highest High - Lowest Low), smoothK)
    %D = SMA(%K, periodD)

    Sources:
        https://www.tradingview.com/wiki/Stochastic_(STOCH)

    Args:
        period (int) Default: 14
        slow (int) Default: 3
        smoothing (int) Default: 3

    """

    indicator_name: str = "STOCH"
    period: int = 14
    slow_period: int = 3
    smoothing_k: int = 3
    input_value: str = "close"

    def _generate_name(self) -> str:
        return f"{self.indicator_name}_{self.period}"

    def _validate_fields(self):
        return

    def _initialise(self):
        self._add_managed_indicator(
            "k",
            SMA(
                candles=self.candles,
                input_value=f"{self.name}.stoch",
                period=self.smoothing_k,
                fullname_override=f"{self.indicator_name}_k",
            ),
        )
        self._add_managed_indicator(
            "d",
            SMA(
                candles=self.candles,
                input_value=f"{self.name}.k",
                period=self.slow_period,
                fullname_override=f"{self.indicator_name}_d",
            ),
        )

    def _calculate_reading(self, index: int) -> float | dict | None:
        if self.reading_period(self.period, self.input_value):
            lowest = min(
                self.reading("low", i) for i in range(index - (self.period - 1), index + 1)
            )
            highest = max(
                self.reading("high", i) for i in range(index - (self.period - 1), index + 1)
            )

            stoch = ((self.reading(self.input_value) - lowest) / (highest - lowest)) * 100

            self.candles[index].indicators[self.name] = {"stoch": stoch}
            self._managed_indictor("k").calculate_index(index)
            k = self.reading(f"{self.indicator_name}_k")

            self.candles[index].indicators[self.name] = {"stoch": stoch, "k": k}
            self._managed_indictor("d").calculate_index(index)
            d = self.reading(f"{self.indicator_name}_d")

            return {"stoch": stoch, "k": k, "d": d}

        return {"stoch": None, "k": None, "d": None}
