from dataclasses import dataclass

from hexital.types import Indicator
from hexital.utilities import candles_sum


@dataclass(kw_only=True)
class RMA(Indicator):
    """wildeR's Moving Average (RMA)

    The WildeR's Moving Average is simply an Exponential Moving Average (EMA) with
    a modified alpha = 1 / length.

    Sources:
        https://tlc.thinkorswim.com/center/reference/Tech-Indicators/studies-library/V-Z/WildersSmoothing
        https://www.incrediblecharts.com/indicators/wilder_moving_average.php

    Args:
        Input value (str): Default Close
        period (int) Default: 10

    """

    indicator_name: str = "RMA"
    input_value: str = "close"
    period: int = 10

    def _generate_name(self) -> str:
        return f"{self.indicator_name}_{self.period}"

    def _calculate_new_reading(self, index: int = -1) -> float | dict | None:
        if self.prev_exists(index):
            return (
                self.get_reading_by_index(index - 1)
                + (
                    self.get_reading_by_index(index, self.input_value)
                    - self.get_reading_by_index(index - 1)
                )
                / self.period
            )
        if self.get_reading_period(self.period, index=index, name=self.input_value):
            return (
                candles_sum(
                    self.candles, self.input_value, length=self.period, index=index
                )
                / self.period
            )

        return None
