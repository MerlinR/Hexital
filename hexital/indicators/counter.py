from dataclasses import dataclass, field
from typing import Any

from ..core.indicator import Indicator, Source


@dataclass(kw_only=True)
class Counter(Indicator[int]):
    """Counter

    Simple Indictor which will count the current streak of a given value,
    specifically designed for bool values, but useable on any other re-occurring values.
    E.G Count the streak for current input value == count_value

    Output type: `float`

    Args:
        source (str): Which input field to calculate the Indicator.
        count_value (bool | int): Which value to be counting, E.G `bool`, `1`, etc
    """

    _name: str = field(init=False, default="COUNT")
    source: Source
    count_value: Any = True

    def _calculate_reading(self, index: int) -> int:
        count = self.prev_reading(default=0)
        reading = self.src(default=count)

        return count + 1 if self.count_value == reading else 0
