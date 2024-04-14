import math
from dataclasses import dataclass, field

from hexital.core.indicator import Indicator, Managed
from hexital.indicators.wma import WMA


@dataclass(kw_only=True)
class HMA(Indicator):
    """Hull Moving Average

    Sources:
        https://school.stockcharts.com/doku.php?id=technical_indicators:hull_moving_average

    """

    _name: str = field(init=False, default="HMA")
    period: int = 10
    input_value: str = "close"

    def _generate_name(self) -> str:
        return f"{self._name}_{self.period}"

    def _initialise(self):
        self.add_sub_indicator(WMA(period=self.period, fullname_override=f"{self._name}_WMA"))

        self.add_sub_indicator(
            WMA(period=int(self.period / 2), fullname_override=f"{self._name}_WMAh")
        )
        self.add_managed_indicator("raw_HMA", Managed(fullname_override="raw_HMA"))
        self.add_managed_indicator(
            "smoothed_HMA",
            WMA(
                input_value="raw_HMA",
                period=int(math.sqrt(self.period)),
                fullname_override="smoothed_HMA",
            ),
        )

    def _calculate_reading(self, index: int) -> float | dict | None:
        if self.reading(f"{self._name}_WMA"):
            raw_hma = (2 * self.reading(f"{self._name}_WMAh")) - self.reading(f"{self._name}_WMA")
            self.managed_indicators["raw_HMA"].set_reading(raw_hma)
            self.managed_indicators["smoothed_HMA"].calculate_index(index)
            return self.reading("smoothed_HMA")

        return None
