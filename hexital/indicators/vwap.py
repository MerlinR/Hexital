from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional

from hexital.core.indicator import Indicator, Managed
from hexital.exceptions import InvalidConfiguration
from hexital.utils.timeframe import TimeFrame, convert_timeframe_to_timedelta, round_down_timestamp

# @dataclass(kw_only=True)
# class VWAP(Indicator):
#     """Volume-Weighted Average Price

#     Sources:
#         https://www.investopedia.com/terms/v/vwap.asp

#     """

#     _name: str = field(init=False, default="VWAP")
#     anchor: Optional[str | TimeFrame | timedelta | int] = "D"

#     def _generate_name(self) -> str:
#         return f"{self._name}_{self.anchor}"

#     def _validate_fields(self):
#         anchor = convert_timeframe_to_timedelta(self.anchor)
#         if not anchor:
#             raise InvalidConfiguration(f"Anchor is Invalid: {anchor}")
#         self.anchor = anchor

#     def _initialise(self):
#         self.add_managed_indicator("VWAP_data", Managed(fullname_override=f"{self.name}_data"))

#     def _calculate_reading(self, index: int) -> float | dict | None:
#         typical_price = (self.reading("high") + self.reading("low") + self.reading("close")) / 3

#         prev_pv = 0
#         prev_vol = 0

#         if self.prev_exists(f"{self.name}_data.pv"):
#             prev_pv = self.prev_reading(f"{self.name}_data.pv")
#             prev_vol = self.prev_reading(f"{self.name}_data.vol")

#         self.managed_indicators["VWAP_data"].set_reading(
#             {
#                 "pv": prev_pv + self.reading("volume") * typical_price,
#                 "vol": prev_vol + self.reading("volume"),
#             }
#         )

#         return self.reading(f"{self.name}_data.pv") / self.reading(f"{self.name}_data.vol")


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
        prev_pv = 0
        prev_vol = 0
        prev_anchor = None

        current_anchor = round_down_timestamp(self.reading("timestamp"), self.anchor)
        typical_price = (self.reading("high") + self.reading("low") + self.reading("close")) / 3

        if self.prev_exists(f"{self.name}_data.active_anchor"):
            prev_anchor = datetime.fromtimestamp(
                self.prev_reading(f"{self.name}_data.active_anchor")
            )

        if prev_anchor == current_anchor and self.prev_exists(f"{self.name}_data.pv"):
            prev_pv = self.prev_reading(f"{self.name}_data.pv")
            prev_vol = self.prev_reading(f"{self.name}_data.vol")

        pv = prev_pv + self.reading("volume") * typical_price
        vol = prev_vol + self.reading("volume")

        self.managed_indicators["VWAP_data"].set_reading(
            {
                "pv": pv,
                "vol": vol,
                "active_anchor": current_anchor.timestamp(),
            }
        )

        return pv / vol
