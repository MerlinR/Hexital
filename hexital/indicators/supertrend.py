from dataclasses import dataclass, field
from typing import cast

from ..core.indicator import Indicator, Source
from .atr import ATR
from .hla import HLA


@dataclass(kw_only=True)
class Supertrend(Indicator[dict[str, float | int | None]]):
    """Supertrend

    It is used to identify market trends and potential entry and exit points in trading.
    The indicator is based on two dynamic values, period and multiplier, and incorporates
    the concept of Average True Range (ATR) to measure market volatility.
    The SuperTrend Indicator generates buy and sell signals by plotting a line on the price chart.

    Output type: `Dict["trend": float, "direction": int, "short": float]`

    Args:
        period (int): How many Periods to use. Defaults to 7
        source (str): Which input field to calculate the Indicator. Defaults to "close"
        multiplier (float): A positive float to multiply the ATR. Defaults to 3.0
    """

    _name: str = field(init=False, default="Supertrend")
    period: int = 7
    source: Source = "close"
    multiplier: float = 3.0


    def _initialise(self):
        self.sub_atr = self.add_child(ATR(period=self.period))
        self.sub_hl = self.add_child(HLA())
        self._state = self.add_state()

    def _calculate_reading(self, index: int) -> dict[str, float | int | None]:
        direction: int = 1
        trend: float | None = None
        long: float | None = None
        short: float | None = None

        atr_ = self.sub_atr.reading()

        if atr_ is None:
            return {"trend": None, "direction": direction, "long": None, "short": None}

        mid_atr = self.multiplier * atr_

        hl = self.sub_hl.reading()
        upper = hl + mid_atr
        lower = hl - mid_atr

        prev_upper = self._state.prev("upper")
        prev_lower = self._state.prev("lower")

        if self._state.prev_exists("lower"):
            close = self.candles[index].close
            if close > prev_upper:
                direction = 1
            elif close < prev_lower:
                direction = -1
            else:
                direction = cast(int, self._state.prev("direction"))

                if direction == 1 and lower < prev_lower:
                    lower = prev_lower
                if direction == -1 and upper > prev_upper:
                    upper = prev_upper

        self._state.set({"upper": upper, "lower": lower, "direction": direction})

        trend = lower if direction == 1 else upper
        long = lower if direction == 1 else None
        short = upper if direction == -1 else None

        return {"trend": trend, "direction": direction, "long": long, "short": short}
