from dataclasses import dataclass, field

from hexital.core.indicator import Indicator


@dataclass(kw_only=True)
class RMA(Indicator):
    """wildeR's Moving Average - RMA

    Wilder's Moving Average places more emphasis on recent price movements than other moving averages.
    This makes it a more responsive tool for short-term traders who need to adapt quickly to
    changing market conditions.

    Sources:
        https://tlc.thinkorswim.com/center/reference/Tech-Indicators/studies-library/V-Z/WildersSmoothing
        https://www.incrediblecharts.com/indicators/wilder_moving_average.php

    Output type: `float`

    Args:
        period (int): How many Periods to use. Defaults to 10
        source (str): Which input field to calculate the Indicator. Defaults to "close"
    """

    _name: str = field(init=False, default="RMA")
    period: int = 10
    source: str = "close"
    _alpha: float = field(init=False, default=0)

    def _generate_name(self) -> str:
        return f"{self._name}_{self.period}"

    def _validate_fields(self):
        self._alpha = float(1.0 / self.period)

    def _calculate_reading(self, index: int) -> float | dict | None:
        if self.prev_exists():
            return float(
                (self._alpha * self.reading(self.source))
                + ((1.0 - self._alpha) * self.prev_reading())
            )

        if self.reading_period(self.period, self.source):
            period_to = index - self.period

            # numpy ewm adjusted calc
            values = sum(
                ((1 - self._alpha) ** py) * self.reading(self.source, i)
                for py, i in enumerate(range(index, period_to, -1))
            )

            divide_by = sum(
                (1 - self._alpha) ** i for py, i in enumerate(range(index, period_to, -1))
            )

            return values / divide_by

        return None
