from dataclasses import dataclass, field
from typing import Optional

from hexital.core.indicator import Indicator, Managed
from hexital.indicators.ema import EMA


@dataclass(kw_only=True)
class TSI(Indicator):
    """True Strength Index - TSI
    TSI attempts to show both trend direction and overbought/oversold conditions,
    using moving averages of the underlying momentum of a financial instrument.

    Sources:
        https://school.stockcharts.com/doku.php?id=technical_indicators:true_strength_index

    Output type: `float`

    Args:
        period (int): How many Periods to use. Defaults to 25
        smooth_period (int): How much to smooth with EMA defaults: (period / 2) + (period % 2 > 0). Defaults to halve of period
        source (str): Which input field to calculate the Indicator. Defaults to "close"

    """

    _name: str = field(init=False, default="TSI")
    period: int = 25
    smooth_period: Optional[int] = None
    source: str = "close"

    def _generate_name(self) -> str:
        return f"{self._name}_{self.period}_{self.smooth_period}"

    def _validate_fields(self):
        if not self.smooth_period:
            self.smooth_period = int(int(self.period / 2) + (self.period % 2 > 0))

    def _initialise(self):
        self.add_managed_indicator("data", Managed(name=f"{self.name}_data"))

        self.managed_indicators["data"].add_sub_indicator(
            EMA(
                source=f"{self.name}_data.price",
                period=self.period,
                name=f"{self.name}_first",
            ),
            False,
        )

        self.managed_indicators["data"].sub_indicators[f"{self.name}_first"].add_sub_indicator(
            EMA(
                source=f"{self.name}_first",
                period=self.smooth_period,
                name=f"{self.name}_second",
            ),
            False,
        )

        self.managed_indicators["data"].add_sub_indicator(
            EMA(
                source=f"{self.name}_data.abs_price",
                period=self.period,
                name=f"{self.name}_abs_first",
            ),
            False,
        )
        self.managed_indicators["data"].sub_indicators[f"{self.name}_abs_first"].add_sub_indicator(
            EMA(
                source=f"{self.name}_abs_first",
                period=self.smooth_period,
                name=f"{self.name}_abs_second",
            ),
            False,
        )

    def _calculate_reading(self, index: int) -> float | dict | None:
        prev_reading = self.prev_reading(self.source)
        if prev_reading is None:
            return None

        source = self.reading(self.source)

        self.managed_indicators["data"].set_reading(
            {
                "price": source - prev_reading,
                "abs_price": abs(source - prev_reading),
            }
        )

        abs_second = self.reading(f"{self.name}_abs_second")
        if abs_second is not None:
            return 100 * (self.reading(f"{self.name}_second") / abs_second)

        return None
