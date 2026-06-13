from __future__ import annotations

import weakref
from collections.abc import Generator, Iterable, MutableSequence, Sequence
from typing import Generic, SupportsIndex, TypeVar

T = TypeVar("T")


class WeakList(MutableSequence[T], Generic[T]):
    _refs: list[weakref.ReferenceType[T]]
    _dirty: bool

    def __init__(self, seq: Sequence[T] | None = None):
        self._refs = []
        self._dirty = False
        if seq:
            self.extend(seq)

    def _mark_dirty(self, _):
        self._dirty = True

    def _ensure_clean(self):
        if self._dirty:
            self.flush()

    def _ref(self, obj: T) -> weakref.ReferenceType[T]:
        return weakref.ref(obj, self._mark_dirty)

    def flush(self):
        self._refs = [ref for ref in self._refs if ref() is not None]
        self._dirty = False

    def reset(self):
        self._refs = []
        self._dirty = False

    def __getitem__(self, idx: slice | SupportsIndex) -> T | list[T]:
        self._ensure_clean()
        if isinstance(idx, SupportsIndex):
            return self._refs[idx]()
        return [ref() for ref in self._refs[idx]]

    def __iter__(self) -> Generator[T]:
        self._ensure_clean()
        for ref in self._refs:
            yield ref()

    def __eq__(self, obj: object) -> bool:
        if not isinstance(obj, Sequence):
            return False
        return list(self) == list(obj)

    def __repr__(self):
        return "WeakList(%r)" % list(self)

    def __len__(self) -> int:
        self._ensure_clean()
        return len(self._refs)

    def __setitem__(self, idx, obj):
        self._ensure_clean()
        if isinstance(idx, slice):
            self._refs[idx] = [self._ref(item) for item in obj]
        else:
            self._refs[idx] = self._ref(obj)

    def __delitem__(self, idx):
        self._ensure_clean()
        del self._refs[idx]

    def append(self, obj: T):
        self._refs.append(self._ref(obj))

    def extend(self, items: Iterable[T]):
        self._refs.extend(self._ref(item) for item in items)

    def insert(self, idx: int, obj: T):
        self._ensure_clean()
        self._refs.insert(idx, self._ref(obj))

    def pop(self, index: SupportsIndex = -1) -> T | None:
        self._ensure_clean()
        obj = self._refs[index]()
        del self._refs[index]
        return obj

    def remove(self, obj):
        self._ensure_clean()
        for i, x in enumerate(self):
            if x == obj:
                del self[i]
                return
        raise ValueError(f"{obj!r} not in WeakList")

    def reverse(self):
        self._ensure_clean()
        self._refs.reverse()

    def __add__(self, other) -> WeakList[T]:
        list_ = WeakList(self)
        list_.extend(other)
        return list_

    def __iadd__(self, other) -> WeakList[T]:
        self.extend(other)
        return self

    def __contains__(self, obj) -> bool:
        return obj in list(self)

    def __mul__(self, n) -> WeakList[T]:
        return WeakList(list(self) * n)

    def __imul__(self, n) -> WeakList[T]:
        self._ensure_clean()
        self._refs *= n
        return self
