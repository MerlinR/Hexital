from dataclasses import dataclass, field
from math import log

from ..core.indicator import Indicator
from ..utils.common import non_zero_range


@dataclass(kw_only=True)
class Fisher(Indicator[dict[str, float | None]]):
    """Fisher Transform - FISHERT

    Fisher Transform converts price position inside a rolling range into a
    Gaussian-like oscillator with a lagged signal line.

    Sources:
        https://tradingstrategy.ai/docs/api/technical-analysis/momentum/help/pandas_ta.momentum.fisher.html

    Output type: `Dict["FISHERT": float, "signal": float]`
    """

    _name: str = field(init=False, default="FISHERT")
    period: int = 9
    signal_period: int = 1

    def _name_parts(self) -> list[str]:
        return ["period", "signal_period"]

    def _initialise(self):
        self._state = self.add_state()

    def _calculate_reading(self, index: int) -> dict[str, float | None]:
        if not self.reading_period(self.period, "high", index):
            return {"FISHERT": None, "signal": None}

        hl2 = 0.5 * (self.high + self.low)
        lowest_hl2 = min(
            0.5 * (self.candles[i].high + self.candles[i].low)
            for i in range(index - self.period + 1, index + 1)
        )
        highest_hl2 = max(
            0.5 * (self.candles[i].high + self.candles[i].low)
            for i in range(index - self.period + 1, index + 1)
        )
        hlr = max(non_zero_range(highest_hl2, lowest_hl2), 0.001)
        position = ((hl2 - lowest_hl2) / hlr) - 0.5

        if index == self.period - 1:
            fisher = 0.0
            self._state.set({"v": 0.0, "fisher": fisher})
            return {"FISHERT": fisher, "signal": None}

        v = 0.66 * position + (0.67 * self._state.prev("v", 0.0))
        if v < -0.99:
            v = -0.999
        elif v > 0.99:
            v = 0.999
        prev_fisher = self._state.prev("fisher", 0.0)
        fisher = 0.5 * (log((1 + v) / (1 - v)) + prev_fisher)
        self._state.set({"v": v, "fisher": fisher})

        signal = self.reading(
            self._state.source("fisher"),
            index=index - self.signal_period,
            default=None,
        )
        return {"FISHERT": fisher, "signal": signal}
