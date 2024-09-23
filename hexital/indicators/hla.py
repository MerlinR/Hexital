from dataclasses import dataclass, field

from hexital.core.indicator import Indicator


@dataclass(kw_only=True)
class HLA(Indicator):
    """High Low Average - HLA

    Output type: `float`
    """

    _name: str = field(init=False, default="HLA")

    def _generate_name(self) -> str:
        return f"{self._name}"

    def _calculate_reading(self, index: int) -> float | dict | None:
        return (self.candles[index].high + self.candles[index].low) / 2
