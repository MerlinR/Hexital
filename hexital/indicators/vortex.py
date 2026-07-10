from dataclasses import dataclass, field

from ..core.indicator import Indicator
from .tr import TR


@dataclass(kw_only=True)
class Vortex(Indicator[dict[str, float | None]]):
    """Vortex Indicator - VTX

    Vortex compares directional movement against total true range to highlight
    bullish and bearish trend dominance.

    Sources:
        https://tradingstrategy.ai/docs/api/technical-analysis/trend/help/pandas_ta.trend.vortex.html

    Output type: `Dict["VTXP": float, "VTXM": float]`

    Args:
        period (int): Rolling window length. Defaults to 14.
        drift (int): Previous candle offset for movement comparison. Defaults to 1.
    """

    _name: str = field(init=False, default="VTX")
    period: int = 14
    drift: int = 1

    def _name_parts(self) -> list[str]:
        return ["period", "drift"]

    def _initialise(self):
        self.sub_tr = self.add_child(TR())
        self._state = self.add_state()

    def _calculate_reading(self, index: int) -> dict[str, float | None]:
        if index < self.drift:
            return {"VTXP": None, "VTXM": None}

        tr = self.sub_tr.reading()
        if tr is None:
            return {"VTXP": None, "VTXM": None}

        prev_candle = self.candles[index - self.drift]
        self._state.set(
            {
                "vmp": abs(self.high - prev_candle.low),
                "vmm": abs(self.low - prev_candle.high),
                "tr": tr,
            }
        )

        if not self.reading_period(self.period, self._state.source("tr"), index):
            return {"VTXP": None, "VTXM": None}

        tr_sum = self.candles_sum(self.period, self._state.source("tr"))
        if tr_sum == 0:
            return {"VTXP": None, "VTXM": None}

        return {
            "VTXP": self.candles_sum(self.period, self._state.source("vmp")) / tr_sum,
            "VTXM": self.candles_sum(self.period, self._state.source("vmm")) / tr_sum,
        }
