from dataclasses import dataclass

from hexital.indicators import Managed
from hexital.types import Indicator


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
        self.add_managed_indicator(
            "VWAP_PV",
            Managed(indicator_name="VWAP_PV", candles=self.candles),
        )
        self.add_managed_indicator(
            "VWAP_Vol",
            Managed(indicator_name="VWAP_Vol", candles=self.candles),
        )

    def _calculate_reading(self, index: int = -1) -> float | dict | None:

        typical_price = (
            self.reading("high") + self.reading("low") + self.reading("close")
        ) / 3

        prev_pv = 0
        prev_vol = 0
        if self.prev_reading("volume"):
            prev_pv = self.managed_indictor("VWAP_PV").reading(index=index - 1)
            prev_vol = self.managed_indictor("VWAP_Vol").reading(index=index - 1)

        self.managed_indictor("VWAP_PV").set_reading(
            index, prev_pv + self.reading("volume") * typical_price
        )
        self.managed_indictor("VWAP_Vol").set_reading(
            index, prev_vol + self.reading("volume")
        )

        return self.managed_indictor("VWAP_PV").reading(
            index=index
        ) / self.managed_indictor("VWAP_Vol").reading(index=index)
