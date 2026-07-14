from __future__ import annotations

from .. import Reading
from ..constants import NESTED_DELI, join_nested_name
from .core import Indicator


class NestedSource:
    indicator: Indicator
    nested_name: str

    def __init__(self, indicator: Indicator, nested_name: str):
        self.indicator = indicator
        self.nested_name = nested_name

    @property
    def candles(self):
        return self.indicator.candles

    @property
    def name(self):
        return join_nested_name(self.indicator.name, self.nested_name)

    @property
    def source_name(self):
        return self.name.replace(NESTED_DELI, "-")

    def reading(self, index: int | None = None) -> Reading:  # type: ignore
        value = self.indicator.reading(index=index)
        if isinstance(value, dict):
            return value.get(self.nested_name)  # type: ignore
        return value

    def series(self) -> list[Reading]:
        return [
            v.get(self.nested_name) if isinstance(v, dict) else v
            for v in self.indicator.series()
        ]

    def __str__(self):
        return join_nested_name(self.indicator.name, self.nested_name)
