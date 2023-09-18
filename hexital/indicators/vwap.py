from dataclasses import dataclass

from hexital.core import Indicator
from hexital.indicators import Managed


@dataclass(kw_only=True)
class VWAP(Indicator):
    """Volume-Weighted Average Price

    Sources:
        https://www.investopedia.com/terms/v/vwap.asp

    """

    indicator_name: str = "VWAP"
    period: int = 10

    def _generate_name(self) -> str:
        return f"{self.indicator_name}_{self.period}"

    def _initialise(self):
        self._add_managed_indicator(
            "VWAP_PV",
            Managed(indicator_name="VWAP_PV", candles=self.candles),
        )
        self._add_managed_indicator(
            "VWAP_Vol",
            Managed(indicator_name="VWAP_Vol", candles=self.candles),
        )

    def _calculate_reading(self, index: int) -> float | dict | None:

        typical_price = (
            self.reading("high") + self.reading("low") + self.reading("close")
        ) / 3

        prev_pv = 0
        prev_vol = 0
        if self.prev_reading("VWAP_PV"):
            prev_pv = self.prev_reading("VWAP_PV")
            prev_vol = self.prev_reading("VWAP_Vol")

        self._managed_indictor("VWAP_PV").set_reading(
            prev_pv + self.reading("volume") * typical_price
        )
        self._managed_indictor("VWAP_Vol").set_reading(prev_vol + self.reading("volume"))

        return self.reading("VWAP_PV") / self.reading("VWAP_Vol")
