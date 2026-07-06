from dataclasses import dataclass, field

from ..core.indicator import Indicator, Source
from ..utils.common import linear_regression_stats


@dataclass(kw_only=True)
class RegressionChannel(Indicator[dict[str, float | None]]):
    """Regression Channel

    Regression Channel fits a rolling least-squares line and places upper and
    lower bands around it using the residual standard deviation.

    Output type: `Dict["lower": float, "mid": float, "upper": float]`

    Args:
        period (int): Rolling window length. Defaults to 14.
        source (str): Which input field to calculate the indicator from.
            Defaults to `"close"`.
        std (float): Residual standard deviation multiplier. Defaults to 2.0.
    """

    _name: str = field(init=False, default="RegressionChannel")
    period: int = 14
    source: Source = "close"
    std: float = 2.0

    def _generate_name(self) -> str:
        return f"{self._name}_{self.period}_{self.std}"

    def _calculate_reading(self, index: int) -> dict[str, float | None]:
        if not self.reading_period(self.period, self.source, index):
            return {"lower": None, "mid": None, "upper": None}

        values = [self.at_src(i) for i in range(index - self.period + 1, index + 1)]
        if any(value is None for value in values):
            return {"lower": None, "mid": None, "upper": None}

        stats = linear_regression_stats(values)
        band = stats.residual_stdev * self.std
        return {
            "lower": stats.line - band,
            "mid": stats.line,
            "upper": stats.line + band,
        }
