from dataclasses import dataclass, field

from ..core.indicator import Indicator


@dataclass(kw_only=True)
class UO(Indicator[float | None]):
    """Ultimate Oscillator - UO

    The Ultimate Oscillator blends short, medium, and long buying pressure
    ratios to reduce false divergence signals from single-window oscillators.

    Sources:
        https://tradingstrategy.ai/docs/api/technical-analysis/momentum/help/pandas_ta.momentum.uo.html

    Output type: `float`

    Args:
        fast (int): Fast lookback. Defaults to 7.
        medium (int): Medium lookback. Defaults to 14.
        slow (int): Slow lookback. Defaults to 28.
        fast_w (float): Fast period weight. Defaults to 4.0.
        medium_w (float): Medium period weight. Defaults to 2.0.
        slow_w (float): Slow period weight. Defaults to 1.0.
    """

    _name: str = field(init=False, default="UO")
    fast: int = 7
    medium: int = 14
    slow: int = 28
    fast_w: float = 4.0
    medium_w: float = 2.0
    slow_w: float = 1.0

    def _name_parts(self) -> list[str]:
        return ["fast", "medium", "slow"]

    def _minimum_candles(self) -> int:
        return self.slow

    def _initialise(self):
        self._state = self.add_state()

    def _calculate_reading(self, index: int) -> float | None:
        if index == 0:
            return None

        prev_close = self.candles[index - 1].close
        max_h_or_pc = max(self.high, prev_close)
        min_l_or_pc = min(self.low, prev_close)

        bp = self.close - min_l_or_pc
        tr = max_h_or_pc - min_l_or_pc
        self._state.set({"bp": bp, "tr": tr})

        if not self.reading_period(self.slow, self._state.source("tr"), index):
            return None

        fast_tr = self.candles_sum(self.fast, self._state.source("tr"))
        medium_tr = self.candles_sum(self.medium, self._state.source("tr"))
        slow_tr = self.candles_sum(self.slow, self._state.source("tr"))

        if fast_tr == 0 or medium_tr == 0 or slow_tr == 0:
            return None

        fast_avg = self.candles_sum(self.fast, self._state.source("bp")) / fast_tr
        medium_avg = self.candles_sum(self.medium, self._state.source("bp")) / medium_tr
        slow_avg = self.candles_sum(self.slow, self._state.source("bp")) / slow_tr

        total_weight = self.fast_w + self.medium_w + self.slow_w
        weights = (
            (self.fast_w * fast_avg)
            + (self.medium_w * medium_avg)
            + (self.slow_w * slow_avg)
        )

        return 100 * weights / total_weight
