from __future__ import annotations

from weakref import ref


class ChildRegistry:
    """Reference-counted registry of child indicators shared across a candle manager."""

    def __init__(self) -> None:
        self._registry: dict[str, "Indicator"] = {}
        self._parents: dict[str, set[str]] = {}

    def attach(self, indicator: "Indicator", parent_fingerprint: str) -> "Indicator":
        fingerprint = indicator.fingerprint
        if existing := self._registry.get(fingerprint):
            self._parents.setdefault(fingerprint, set()).add(parent_fingerprint)
            return existing

        self._registry[fingerprint] = indicator
        self._parents[fingerprint] = {parent_fingerprint}
        return indicator

    def release(self, child_fingerprint: str, parent_fingerprint: str) -> bool:
        """Drop one parent link; return True when candle data may be purged."""
        parents = self._parents.get(child_fingerprint)
        if not parents or parent_fingerprint not in parents:
            return False

        parents.discard(parent_fingerprint)
        if parents:
            return False

        self._parents.pop(child_fingerprint, None)
        self._registry.pop(child_fingerprint, None)
        return True

    def release_parent(self, parent_fingerprint: str) -> set[str]:
        """Release all children linked to a parent; return names to purge from candles."""
        purge_names: set[str] = set()
        for child_fingerprint in list(self._parents):
            if parent_fingerprint not in self._parents[child_fingerprint]:
                continue
            child_name = self._registry[child_fingerprint].name
            if self.release(child_fingerprint, parent_fingerprint):
                purge_names.add(child_name)
        return purge_names


_registries: dict[int, ChildRegistry] = {}


def child_registry_for(manager: "CandleManager") -> ChildRegistry:
    """Return the shared child registry for indicators on the same candle manager."""
    key = id(manager)
    registry = _registries.get(key)
    if registry is None:
        registry = ChildRegistry()
        _registries[key] = registry

        def _cleanup(_reference, registry_key: int = key) -> None:
            _registries.pop(registry_key, None)

        ref(manager, _cleanup)
    return registry
