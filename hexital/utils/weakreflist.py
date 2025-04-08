from __future__ import annotations

import weakref
from collections.abc import Sequence
from typing import Generator, Generic, List, Optional, SupportsIndex, TypeVar

T = TypeVar("T")


class WeakList(Generic[T], list):
    _refs: List[weakref.ReferenceType[T]]
    _dirty: bool

    def __init__(self, seq: Optional[Sequence] = None):
        list.__init__(self)
        self._refs = []
        self._dirty = False
        if seq:
            for x in seq:
                self.append(x)

    def _mark_dirty(self, _):
        self._dirty = True

    def flush(self):
        self._refs = [x for x in self._refs if x() is not None]
        self._dirty = False

    def reset(self):
        self._refs = []
        self._dirty = False

    def __getitem__(self, idx: slice | SupportsIndex) -> T | List[T]:
        if self._dirty:
            self.flush()
        if isinstance(idx, SupportsIndex):
            return self._refs[idx]()
        else:
            return [v() for v in self._refs[idx]]

    def __iter__(self) -> Generator[T, None, None]:
        for ref in self._refs:
            obj = ref()
            if obj is not None:
                yield obj

    def __eq__(self, obj: object) -> bool:
        if not isinstance(obj, Sequence):
            return False
        if len(self._refs) != len(obj):
            return False
        for idx in range(len(self._refs)):
            if obj[idx] != self._refs[idx]():
                return False
        return True

    def __repr__(self):
        return "WeakList(%r)" % list(self)

    def __len__(self) -> int:
        if self._dirty:
            self.flush()
        return len(self._refs)

    def __setitem__(self, idx, obj):
        if isinstance(idx, slice):
            self._refs[idx] = [weakref.ref(obj, self._mark_dirty) for x in obj]
        else:
            self._refs[idx] = weakref.ref(obj, self._mark_dirty)

    def __delitem__(self, idx):
        del self._refs[idx]

    def append(self, obj):
        self._refs.append(weakref.ref(obj, self._mark_dirty))

    def extend(self, items):
        for x in items:
            self.append(x)

    def insert(self, idx, obj):
        self._refs.insert(idx, weakref.ref(obj, self._mark_dirty))

    def pop(self, index: SupportsIndex = -1) -> T | None:
        if self._dirty:
            self.flush()
        obj = self._refs[index]()
        del self._refs[index]
        return obj

    def remove(self, obj):
        if self._dirty:
            self.flush()
        for i, x in enumerate(self):
            if x == obj:
                del self[i]

    def reverse(self):
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
        self._refs *= n
        return self
