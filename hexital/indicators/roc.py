from dataclasses import dataclass, field

from hexital.core.indicator import Indicator


@dataclass(kw_only=True)
class ROC(Indicator):
    """Rate Of Change"""

    _name: str = field(init=False, default="ROC")
    period: int = 10
    input_value: str = "close"

    def _generate_name(self) -> str:
        return f"{self._name}"

    def _calculate_reading(self, index: int) -> float | dict | None:
        if self.prev_exists() or self.reading_period(self.period + 1, "close"):
            period_n_back = self.reading(self.input_value, index - self.period)

            return ((self.reading(self.input_value) - period_n_back) / period_n_back) * 100
        return None
