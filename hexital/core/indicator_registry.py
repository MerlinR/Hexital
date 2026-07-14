from __future__ import annotations

from typing import TypeAlias

ParentRef: TypeAlias = str | object

_registries: dict[int, IndicatorRegistry] = {}


def registry(manager) -> IndicatorRegistry:
    """Return the indicator registry scoped to a candle manager."""
    return _registries.setdefault(id(manager), IndicatorRegistry())


class IndicatorRegistry:
    """Fingerprint-keyed registry of indicators and their parent/child links."""

    def __init__(self) -> None:
        self.indicators: dict[str, "Indicator"] = {}
        self.indicator_references: dict[ParentRef, list[str]] = {}
        self._parents: dict[str, set[ParentRef]] = {}

    def attach(
        self, indicator: "Indicator", parent: ParentRef | None = None
    ) -> "Indicator":
        fingerprint = indicator.fingerprint
        if fingerprint not in self.indicators:
            self.indicators[fingerprint] = indicator

        if parent is not None:
            self._parents.setdefault(fingerprint, set()).add(parent)
            if parent not in self.indicator_references:
                self.indicator_references[parent] = []
            if fingerprint not in self.indicator_references[parent]:
                self.indicator_references[parent].append(fingerprint)

        return self.indicators[fingerprint]

    def get_children(self, parent: ParentRef):
        """Yield direct children of a parent in attachment order."""
        for child_fingerprint in self.indicator_references.get(parent, []):
            if child_fingerprint in self.indicators:
                yield self.indicators[child_fingerprint]

    def get_parent(self, fingerprint: str) -> str | None:
        parents = self._parents.get(fingerprint)
        if not parents:
            return None
        return next(iter(parents))

    def release_parent(self, parent: ParentRef) -> set[str]:
        """Drop a parent's child links; return indicator names safe to purge."""
        child_fingerprints = self.indicator_references.pop(parent, [])
        purge_names: set[str] = set()

        for child_fingerprint in child_fingerprints:
            purge_names.update(self._release_child_link(parent, child_fingerprint))

        return purge_names

    def dettach(self, parent: ParentRef, child_fingerprint: str) -> set[str]:
        """Remove one parent-child link; return indicator names safe to purge."""
        refs = self.indicator_references.get(parent)
        if refs and child_fingerprint in refs:
            refs.remove(child_fingerprint)
            if not refs:
                self.indicator_references.pop(parent, None)

        return self._release_child_link(parent, child_fingerprint)

    def _release_child_link(self, parent: ParentRef, child_fingerprint: str) -> set[str]:
        parents = self._parents.get(child_fingerprint)
        if not parents or parent not in parents:
            return set()

        parents.discard(parent)
        if parents:
            return set()

        self._parents.pop(child_fingerprint, None)
        if indicator := self.indicators.pop(child_fingerprint, None):
            return {indicator.name}
        return set()

    def __contains__(self, fingerprint: str) -> bool:
        return fingerprint in self.indicators
