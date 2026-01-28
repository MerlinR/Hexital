from dataclasses import dataclass, field
from datetime import timedelta

from ..core.indicator import Indicator, Managed, NestedSource
from ..exceptions import InvalidConfiguration
from ..utils.timeframe import (
    TimeFrame,
    convert_timeframe_to_timedelta,
    round_down_timestamp,
    timedelta_to_str,
    validate_timeframe,
)


@dataclass(kw_only=True)
class VWAP(Indicator[float]):
    """Volume-Weighted Average Price - VWAP

    The volume-weighted average price is a technical analysis indicator
    used on intraday charts that resets at the start of every new trading session.
    Resets on the configured anchor timeframe (default: daily "D").

    Sources:
        https://www.investopedia.com/terms/v/vwap.asp

    Output type: `float`

    Args:
        anchor (Optional[str | TimeFrame | timedelta | int]): How to anchor VWAP, Depends on the index values, uses TimeFrame
    """

    _name: str = field(init=False, default="VWAP")
    anchor: str | TimeFrame | timedelta | int | None = "D"

    def _generate_name(self) -> str:
        return f"{self._name}_{timedelta_to_str(self.anchor)}"

    def _validate_fields(self):
        if not validate_timeframe(self.anchor):
            raise InvalidConfiguration(f"Anchor is Invalid: {self.anchor}")

        self.anchor = convert_timeframe_to_timedelta(self.anchor)

    def _initialise(self):
        self.data = self.add_managed_indicator(Managed())

    def _calculate_reading(self, index: int) -> float:
        candle = self.candles[index]
        if not candle.timestamp:
            return 0.0

        current_anchor = round_down_timestamp(candle.timestamp, self.anchor).timestamp()

        prev_anchor = self.prev_reading(NestedSource(self.data, "active_anchor"))
        typical_price = (candle.high + candle.low + candle.close) / 3.0

        if prev_anchor != current_anchor:
            pv = 0.0
            vol = 0.0
        else:
            pv = float(self.prev_reading(NestedSource(self.data, "pv"), 0.0))
            vol = float(self.prev_reading(NestedSource(self.data, "vol"), 0.0))

        pv += candle.volume * typical_price
        vol += candle.volume

        self.data.set_reading({"pv": pv, "vol": vol, "active_anchor": current_anchor})
        return pv / vol if vol != 0 else 0.0
