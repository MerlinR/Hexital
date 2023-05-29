from dataclasses import dataclass

from hexital.types import Indicator


@dataclass(kw_only=True)
class EMA(Indicator):
    period: int
    input_value: str
    multiplier: float = 2.0
    _name: str = "EMA"

    def _gen_name(self) -> str:
        return f"{self._name}_{self.period}"

    def _calculate_new_value(self, index: int = -1) -> float | None:
        if index < self.period - 1:
            return None
        if index == self.period - 1:
            return (
                sum(
                    [
                        self.get_indicator(value, self.input_value)
                        for value in self.candles[0 : index + 1]
                    ]
                )
                / self.period
            )

        mult = self.multiplier / (self.period + 1.0)

        return float(
            mult * self.get_indicator(self.candles[index], self.input_value)
            + (1.0 - mult) * self.get_prev(index)
        )
