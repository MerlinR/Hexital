from dataclasses import dataclass, field

from hexital.core.indicator import Indicator


@dataclass(kw_only=True)
class Counter(Indicator):
    """Counter
    Simple Indictor which will count the current streak of a given value,
    specifically designed for bool values, but useable on any other re-occuring values.
    E.G Count the streak for current input value == count_value

    Args:
        Input value (str)
        Count Value(bool | int): Default True
            - What to check value matches.
    """

    _name: str = field(init=False, default="COUNT")
    input_value: str
    count_value: bool | int = True

    def _generate_name(self) -> str:
        return f"{self._name}_{self.input_value.split('.')[0]}"

    def _calculate_reading(self, index: int) -> float | dict | None:
        reading = self.reading(self.input_value)
        count = self.prev_reading()

        if not count:
            count = 0

        if reading is None:
            return count

        if self.count_value == reading:
            count += 1
        else:
            count = 0

        return count
