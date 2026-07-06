from dataclasses import dataclass, field

from ..core.indicator import Indicator, Source
from ..utils.common import linear_regression_stats


@dataclass(kw_only=True)
class LinearRegression(Indicator[float | None]):
    """Linear Regression - LR

    Linear Regression fits a least-squares line over a rolling window and
    returns the line value using the same convention as `pandas-ta` `linreg`.

    Sources:
        https://tradingstrategy.ai/docs/api/technical-analysis/overlap/help/pandas_ta.overlap.linreg.html

    Output type: `float`

    Args:
        period (int): Rolling window length. Defaults to 14.
        source (str): Which input field to calculate the indicator from.
            Defaults to `"close"`.
    """

    _name: str = field(init=False, default="LinearRegression")
    period: int = 14
    source: Source = "close"

    def _generate_name(self) -> str:
        return f"{self._name}_{self.period}"

    def _calculate_reading(self, index: int) -> float | None:
        if not self.reading_period(self.period, self.source, index):
            return None

        values = [self.at_src(i) for i in range(index - self.period + 1, index + 1)]
        if any(value is None for value in values):
            return None

        return linear_regression_stats(values).line
