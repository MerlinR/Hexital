from dataclasses import dataclass, field

from ..analysis import movement
from ..core.indicator import Indicator, Source
from .sma import SMA


@dataclass(kw_only=True)
class STOCH(Indicator[dict[str, float | None]]):
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
        period (int): How many Periods to use. Defaults to 14
        slow_period (int): How many Periods to use on smoothing d. Defaults to 3
        smoothing_k (int): How many Periods to use on smoothing K. Defaults to 3
        source (str): Which input field to calculate the Indicator. Defaults to "close"
    """

    _name: str = field(init=False, default="STOCH")
    period: int = 14
    slow_period: int = 3
    smoothing_k: int = 3
    source: Source = "close"

    def _name_parts(self) -> list[str]:
        return ["period", "slow_period", "smoothing_k", "source"]

    def _minimum_candles(self) -> int:
        return self.period + self.smoothing_k + self.slow_period - 2

    def _initialise(self):
        self._state = self.add_state()
        self.sub_k = self._state.managed.add_child_after(
            SMA(
                source=self._state.source("stoch"),
                period=self.smoothing_k,
                name=f"{self.name}_k",
            ),
        )
        self.sub_d = self.add_child_managed(
            SMA(
                source=self._state.source("k"),
                period=self.slow_period,
                name=f"{self.name}_d",
            ),
        )

    def _calculate_reading(self, index: int) -> dict[str, float | None]:
        stoch = None
        k = None

        if not self.reading_period(self.period, self.source):
            return {"stoch": None, "k": None, "d": None}

        lowest = movement.lowest(self.candles, "low", self.period, index)
        highest = movement.highest(self.candles, "high", self.period, index)
        reading = self.src()

        if (
            lowest is None
            or highest is None
            or reading is None
            or highest == lowest
        ):
            return {"stoch": None, "k": None, "d": None}

        stoch = ((reading - lowest) / (highest - lowest)) * 100

        self._state.set({"stoch": stoch})
        k = self.sub_k.reading()

        self._state.set({"stoch": stoch, "k": k})

        self.sub_d.calculate_index(index)

        return {"stoch": stoch, "k": k, "d": self.sub_d.reading()}
