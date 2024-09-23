from dataclasses import dataclass, field

from hexital.core.indicator import Indicator


@dataclass(kw_only=True)
class Counter(Indicator):
    """Counter

    Simple Indictor which will count the current streak of a given value,
    specifically designed for bool values, but useable on any other re-occurring values.
    E.G Count the streak for current input value == count_value

    Output type: `float`

    Args:
        input_value: Which input field to calculate the Indicator
        count_value: Which value to be counting, E.G `bool`, `1`, etc
    """

    _name: str = field(init=False, default="COUNT")
    input_value: str
    count_value: bool | int = True

    def _generate_name(self) -> str:
        return f"{self._name}_{self.input_value.split('.')[0]}"

    def _calculate_reading(self, index: int) -> float | dict | None:
        count = self.prev_reading(default=0)
        reading = self.reading(self.input_value, default=count)

        return count + 1 if self.count_value == reading else 0
