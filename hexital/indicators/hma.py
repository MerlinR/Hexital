import math
from dataclasses import dataclass, field

from hexital.core.indicator import Indicator, Managed
from hexital.indicators.wma import WMA


@dataclass(kw_only=True)
class HMA(Indicator):
    """Hull Moving Average - HMA

    It is a combination of weighted moving averages designed
    to be more responsive to current price fluctuations while still smoothing prices.

    Sources:
        https://school.stockcharts.com/doku.php?id=technical_indicators:hull_moving_average

    Output type: `float`

    Args:
        period (int): How many Periods to use. Defaults to 10
        source (str): Which input field to calculate the Indicator. Defaults to "close"

    """

    _name: str = field(init=False, default="HMA")
    period: int = 10
    source: str = "close"

    def _generate_name(self) -> str:
        return f"{self._name}_{self.period}"

    def _initialise(self):
        self.sub_wma = self.add_sub_indicator(
            WMA(
                source=self.source,
                period=self.period,
                name=f"{self.name}_WMA",
            )
        )
        self.sub_wmah = self.add_sub_indicator(
            WMA(
                source=self.source,
                period=int(self.period / 2),
                name=f"{self.name}_WMAh",
            )
        )

        self.sub_hma = self.add_managed_indicator("raw_HMA", Managed(name=f"{self.name}_HMAr"))
        self.sub_hma_smoothed = self.sub_hma.add_sub_indicator(
            WMA(
                source=f"{self.name}_HMAr",
                period=int(math.sqrt(self.period)),
                name=f"{self.name}_HMAs",
            ),
            False,
        )

    def _calculate_reading(self, index: int) -> float | dict | None:
        raw_hma = None
        wma = self.sub_wma.reading()

        if wma is not None:
            raw_hma = (2 * self.sub_wmah.reading()) - wma

        self.sub_hma.set_reading(raw_hma)
        return self.sub_hma_smoothed.reading()
