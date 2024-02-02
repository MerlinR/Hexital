from dataclasses import dataclass, field

from hexital.core.indicator import Indicator


@dataclass(kw_only=True)
class RMA(Indicator):
    """wildeR's Moving Average (RMA)

    Sources:
        https://tlc.thinkorswim.com/center/reference/Tech-Indicators/studies-library/V-Z/WildersSmoothing
        https://www.incrediblecharts.com/indicators/wilder_moving_average.php

    """

    _name: str = field(init=False, default="RMA")
    period: int = 10
    input_value: str = "close"

    def _generate_name(self) -> str:
        return f"{self._name}_{self.period}"

    def _initialise(self):
        return

    def _calculate_reading(self, index: int) -> float | dict | None:
        alpha = float(1.0 / self.period)

        if self.prev_exists():
            return float(
                (alpha * self.reading(self.input_value)) + ((1.0 - alpha) * self.prev_reading())
            )

        if self.reading_period(self.period, self.input_value):
            period_to = index - self.period if index >= (self.period + 1) else -1

            # numpy ewm adjusted calc
            values = sum(
                ((1 - alpha) ** py) * self.reading(self.input_value, i)
                for py, i in enumerate(range(index, period_to, -1))
            )

            divide_by = sum((1 - alpha) ** i for py, i in enumerate(range(index, period_to, -1)))

            return values / divide_by

        return None
