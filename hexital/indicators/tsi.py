from dataclasses import dataclass, field
from typing import Optional

from hexital.core.indicator import Indicator, Managed
from hexital.indicators.ema import EMA


@dataclass(kw_only=True)
class TSI(Indicator):
    """True Strength Index (TSI)

    Sources:
        https://school.stockcharts.com/doku.php?id=technical_indicators:true_strength_index

    """

    _name: str = field(init=False, default="TSI")
    period: int = 25
    smooth_period: Optional[int] = None
    input_value: str = "close"

    def _generate_name(self) -> str:
        return f"{self._name}_{self.period}_{int(self.period/2)}"

    def _validate_fields(self):
        if self.smooth_period is None:
            self.smooth_period = int(self.period / 2) + (self.period % 2 > 0)

    def _initialise(self):
        self.add_managed_indicator("TSI_data", Managed(fullname_override="TSI_data"))

        self.managed_indicators["TSI_data"].add_sub_indicator(
            EMA(
                input_value="TSI_data.price",
                period=self.period,
                fullname_override="TSI_first",
            ),
            False,
        )

        self.managed_indicators["TSI_data"].sub_indicators["TSI_first"].add_sub_indicator(
            EMA(
                input_value="TSI_first",
                period=self.smooth_period,
                fullname_override="TSI_second",
            ),
            False,
        )

        self.managed_indicators["TSI_data"].add_sub_indicator(
            EMA(
                input_value="TSI_data.abs_price",
                period=self.period,
                fullname_override="TSI_abs_first",
            ),
            False,
        )
        self.managed_indicators["TSI_data"].sub_indicators["TSI_abs_first"].add_sub_indicator(
            EMA(
                input_value="TSI_abs_first",
                period=self.smooth_period,
                fullname_override="TSI_abs_second",
            ),
            False,
        )

    def _calculate_reading(self, index: int) -> float | dict | None:
        if not self.reading_period(2, self.input_value):
            return None

        self.managed_indicators["TSI_data"].set_reading(
            {
                "price": self.reading(self.input_value) - self.prev_reading(self.input_value),
                "abs_price": abs(
                    self.reading(self.input_value) - self.prev_reading(self.input_value)
                ),
            }
        )

        if self.reading("TSI_abs_second"):
            return 100 * (self.reading("TSI_second") / self.reading("TSI_abs_second"))

        return None
