from dataclasses import dataclass, field

from ..core.indicator import Indicator
from .atr import ATR
from .rma import RMA


@dataclass(kw_only=True)
class ADX(Indicator[dict[str, float | None]]):
    """Average Directional Index - ADX

    ADX is a trend strength in a series of prices of a financial instrument.

    Sources:
        https://en.wikipedia.org/wiki/Average_directional_movement_index

    Output type: `Dict["ADX": float, "DM_Plus": float, "DM_Neg": float]`

    Args:
        period (int): How many Periods to use. Defaults to 14
        period_signal (Optional[int]):  Average Directional Index period. Defaults same as period
        multiplier (float | None): ADX smoothing multiplier. Defaults to 100.0
    """

    _name: str = field(init=False, default="ADX")

    period: int = 14
    period_signal: int = 0
    multiplier: float = 100.0

    def _generate_name(self) -> str:
        return f"{self._name}_{self.period}_{self.period_signal}"

    def _validate_fields(self):
        if self.period_signal == 0:
            self.period_signal = self.period

    def _initialise(self):
        self.sub_atr = self.add_child(ATR(period=self.period))
        self._state = self.add_state()

        self.sub_pos = self._state.managed.add_child_after(
            RMA(
                name=f"{self.name}_positive",
                period=self.period,
                source=self._state.source("positive"),
            ),
        )
        self.sub_neg = self._state.managed.add_child_after(
            RMA(
                name=f"{self.name}_negative",
                period=self.period,
                source=self._state.source("negative"),
            ),
        )
        self.dx = self.add_child_managed(
            RMA(
                name=f"{self.name}_dx",
                period=self.period_signal,
                source=self._state.source("dx"),
            ),
        )

    def _calculate_reading(self, index: int) -> dict[str, float | None]:
        adx_positive = None
        adx_negative = None
        candle = self.candles[index]
        prev_candle = self.candles[index - 1] if index > 0 else None

        if prev_candle:
            up = candle.high - prev_candle.high
            down = prev_candle.low - candle.low
        else:
            up = 0
            down = 0

        dm_plus = ((up > down) and (up > 0)) * up
        dm_neg = ((down > up) and (down > 0)) * down

        self._state.set({"positive": dm_plus, "negative": dm_neg})

        atr_: float = self.sub_atr.reading()

        if atr_ is None or not self.sub_pos.exists():
            return {"ADX": None, "DM_Plus": None, "DM_Neg": None}

        mod = self.multiplier / atr_

        adx_positive = mod * self.sub_pos.reading()
        adx_negative = mod * self.sub_neg.reading()

        dx = (
            self.multiplier
            * abs(adx_positive - adx_negative)
            / (adx_positive + adx_negative)
        )

        self._state.set({"positive": dm_plus, "negative": dm_neg, "dx": dx})
        self.dx.calculate_index(index)

        return {
            "ADX": self.dx.reading(),
            "DM_Plus": adx_positive,
            "DM_Neg": adx_negative,
        }
