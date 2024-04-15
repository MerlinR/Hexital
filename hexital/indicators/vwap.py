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
        self.add_managed_indicator("VWAP_data", Managed(fullname_override=f"{self.name}_data"))

    def _calculate_reading(self, index: int) -> float | dict | None:
        typical_price = (self.reading("high") + self.reading("low") + self.reading("close")) / 3

        prev_pv = 0
        prev_vol = 0
        if self.prev_exists(f"{self.name}_data.pv"):
            prev_pv = self.prev_reading(f"{self.name}_data.pv")
            prev_vol = self.prev_reading(f"{self.name}_data.vol")

        self.managed_indicators["VWAP_data"].set_reading(
            {
                "pv": prev_pv + self.reading("volume") * typical_price,
                "vol": prev_vol + self.reading("volume"),
            }
        )

        if self.reading(f"{self.name}_data.vol") == 0:
            return self.reading(f"{self.name}_data.pv")
        return self.reading(f"{self.name}_data.pv") / self.reading(f"{self.name}_data.vol")
