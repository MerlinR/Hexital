from dataclasses import dataclass, field
from datetime import timedelta
from typing import Optional

from hexital.core.indicator import Indicator, Managed
from hexital.exceptions import InvalidConfiguration
from hexital.utils.timeframe import TimeFrame, convert_timeframe_to_timedelta, round_down_timestamp


@dataclass(kw_only=True)
class VWAP(Indicator):
    """Volume-Weighted Average Price

    Sources:
        https://www.investopedia.com/terms/v/vwap.asp

    """

    _name: str = field(init=False, default="VWAP")
    anchor: Optional[str | TimeFrame | timedelta | int] = "D"

    def _generate_name(self) -> str:
        return f"{self._name}_{self.anchor}"

    def _validate_fields(self):
        anchor = convert_timeframe_to_timedelta(self.anchor)
        if not anchor:
            raise InvalidConfiguration(f"Anchor is Invalid: {anchor}")
        self.anchor = anchor

    def _initialise(self):
        self.add_managed_indicator("VWAP_data", Managed(fullname_override=f"{self.name}_data"))

    def _calculate_reading(self, index: int) -> float | dict | None:
        candle = self.candles[index]

        current_anchor = round_down_timestamp(self.reading("timestamp"), self.anchor).timestamp()
        prev_anchor = self.prev_reading(f"{self.name}_data.active_anchor")
        typical_price = (candle.high + candle.low + candle.close) / 3.0

        if prev_anchor and prev_anchor == current_anchor:
            pv = self.prev_reading(f"{self.name}_data.pv")
            vol = self.prev_reading(f"{self.name}_data.vol")
        else:
            pv = 0
            vol = 0

        pv = pv + (candle.volume * typical_price)
        vol = vol + candle.volume

        self.managed_indicators["VWAP_data"].set_reading(
            {"pv": pv, "vol": vol, "active_anchor": current_anchor}
        )

        return pv / vol
