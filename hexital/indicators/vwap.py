from dataclasses import dataclass, field

from hexital.core.indicator import Indicator, Managed


@dataclass(kw_only=True)
class VWAP(Indicator):
    """Volume-Weighted Average Price

    Sources:
        https://www.investopedia.com/terms/v/vwap.asp

    """

    _name: str = field(init=False, default="VWAP")
    period: int = 10

    def _generate_name(self) -> str:
        return f"{self._name}_{self.period}"

    def _initialise(self):
        self._add_managed_indicator("VWAP_data", Managed(indicator_name="VWAP_data"))

    def _calculate_reading(self, index: int) -> float | dict | None:
        typical_price = (self.reading("high") + self.reading("low") + self.reading("close")) / 3

        prev_pv = 0
        prev_vol = 0
        if self.prev_reading("VWAP_data.pv"):
            prev_pv = self.prev_reading("VWAP_data.pv")
            prev_vol = self.prev_reading("VWAP_data.vol")

        self._managed_indicators["VWAP_data"].set_reading(
            {
                "pv": prev_pv + self.reading("volume") * typical_price,
                "vol": prev_vol + self.reading("volume"),
            }
        )

        if self.reading("VWAP_data.vol") == 0:
            return self.reading("VWAP_data.pv")
        return self.reading("VWAP_data.pv") / self.reading("VWAP_data.vol")
