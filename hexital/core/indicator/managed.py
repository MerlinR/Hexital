from __future__ import annotations

from dataclasses import dataclass, field

from .. import Reading
from .child_when import ChildWhen
from .core import Indicator, T
from .sources import NestedSource


@dataclass(kw_only=True)
class Managed(Indicator):
    """Managed

    Empty Indicator thats manually controlled and the reading manually set.

    """

    _when: ChildWhen | None = field(init=False, default=ChildWhen.MANUAL)

    def _calculate_reading(self, index: int) -> Reading: ...

    def set_reading(self, reading: Reading, index: int | None = None):  # type: ignore
        if index is None:
            index = self._active_index
        else:
            self.set_active_index(index)

        self._calculate_children(ChildWhen.BEFORE, index)
        self._set_reading(reading, index)  # type: ignore
        self._calculate_children(ChildWhen.AFTER, index)

    def set_active_index(self, index: int):
        self._active_index = index


class State:
    """Internal state backed by a managed child indicator.

    Use via `Indicator.add_state()` rather than constructing directly.
    Dictionary keys map to fields stored on each candle's `sub_indicators`.
    """

    __slots__ = ("_managed", "_parent", "_sources")

    def __init__(self, parent: Indicator, managed: Managed):
        self._parent = parent
        self._managed = managed
        self._sources: dict[str, NestedSource] = {}

    @property
    def managed(self) -> Managed:
        """Underlying managed child, e.g. as an EMA `source`."""
        return self._managed

    def source(self, key: str) -> NestedSource:
        """Reference a state field as an indicator source."""
        if key not in self._sources:
            self._sources[key] = NestedSource(self._managed, key)
        return self._sources[key]

    def prev(self, key: str | None = None, default: T | None = None) -> Reading | T:
        """Previous reading for the whole state or a single field."""
        if key is None:
            return self._parent.prev_reading(self._managed, default)  # type: ignore
        return self._parent.prev_reading(self.source(key), default)  # type: ignore

    def reading(self, key: str | None = None, default: T | None = None) -> Reading | T:
        """Current reading for the whole state or a single field."""
        if key is None:
            value = self._managed.reading()
            return value if value is not None else default  # type: ignore
        return self._parent.reading(self.source(key), default=default)  # type: ignore

    def prev_exists(self, key: str | None = None) -> bool:
        if key is None:
            return self._parent.prev_exists(self._managed)
        return self._parent.prev_exists(self.source(key))

    def exists(self, key: str | None = None) -> bool:
        if key is None:
            return self._managed.exists()
        return self._parent.exists(self.source(key))

    def set(self, reading: Reading, index: int | None = None) -> None:
        """Replace the stored state for the current or given candle."""
        self._managed.set_reading(reading, index=index)  # type: ignore

    def update(self, index: int | None = None, **values: Reading) -> None:
        """Merge fields into dict state for the current or given candle."""
        current = self._parent.reading(self._managed, index=index, default={})
        if isinstance(current, dict):
            self._managed.set_reading({**current, **values}, index=index)  # type: ignore
        else:
            self._managed.set_reading(values, index=index)  # type: ignore
