from dataclasses import dataclass, field

from hexital.analysis import movement
from hexital.core.indicator import Indicator, Managed
from hexital.indicators.sma import SMA


@dataclass(kw_only=True)
class STOCH(Indicator):
    """Stochastic - STOCH

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

    Output type: `Dict["stoch": float, "k": float, "d": float]`

    Args:
        period: How many Periods to use
        slow_period: How many Periods to use on smoothing d
        smoothing_k: How many Periods to use on smoothing K
        input_value: Which input field to calculate the Indicator
    """

    _name: str = field(init=False, default="STOCH")
    period: int = 14
    slow_period: int = 3
    smoothing_k: int = 3
    input_value: str = "close"

    def _generate_name(self) -> str:
        return f"{self._name}_{self.period}"

    def _initialise(self):
        self.add_managed_indicator("data", Managed(fullname_override=f"{self.name}_data"))
        self.managed_indicators["data"].add_sub_indicator(
            SMA(
                input_value=f"{self.name}_data.stoch",
                period=self.smoothing_k,
                fullname_override=f"{self.name}_k",
            ),
            False,
        )
        self.add_managed_indicator(
            "STOCH_d",
            SMA(
                input_value=f"{self.name}_data.k",
                period=self.slow_period,
                fullname_override=f"{self.name}_d",
            ),
        )

    def _calculate_reading(self, index: int) -> float | dict | None:
        stoch = None
        k = None
        d = None

        if self.reading_period(self.period, self.input_value):
            lowest = movement.lowest(self.candles, "low", self.period, index)
            highest = movement.highest(self.candles, "high", self.period, index)

            stoch = ((self.reading(self.input_value) - lowest) / (highest - lowest)) * 100

            self.managed_indicators["data"].set_reading({"stoch": stoch})
            k = self.reading(f"{self.name}_k")

            self.managed_indicators["data"].set_reading({"stoch": stoch, "k": k})
            self.managed_indicators["STOCH_d"].calculate_index(index)
            d = self.reading(f"{self.name}_d")

        return {"stoch": stoch, "k": k, "d": d}
