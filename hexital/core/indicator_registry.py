from __future__ import annotations


class IndicatorRegistry:
    """Global fingerprint-keyed registry of indicators and their parent/child links."""

    def __init__(self) -> None:
        self.indicators: dict[str, "Indicator"] = {}
        self.indicator_references: dict[str, list[str]] = {}
        self._parents: dict[str, set[str]] = {}

    def attach(self, indicator: "Indicator", parent_fingerprint: str | None = None) -> "Indicator":
        fingerprint = indicator.fingerprint
        if fingerprint not in self.indicators:
            self.indicators[fingerprint] = indicator

        if parent_fingerprint:
            self._parents.setdefault(fingerprint, set()).add(parent_fingerprint)
            if parent_fingerprint not in self.indicator_references:
                self.indicator_references[parent_fingerprint] = []
            if fingerprint not in self.indicator_references[parent_fingerprint]:
                self.indicator_references[parent_fingerprint].append(fingerprint)

        return self.indicators[fingerprint]

    def get_children(self, parent_fingerprint: str):
        """Yield direct children of a parent indicator in attachment order."""
        for child_fingerprint in self.indicator_references.get(parent_fingerprint, []):
            if child_fingerprint in self.indicators:
                yield self.indicators[child_fingerprint]

    def get_parent(self, fingerprint: str) -> str | None:
        parents = self._parents.get(fingerprint)
        if not parents:
            return None
        return next(iter(parents))

    def release_parent(self, parent_fingerprint: str) -> set[str]:
        """Drop a parent's child links; return indicator names safe to purge."""
        child_fingerprints = self.indicator_references.pop(parent_fingerprint, [])
        purge_names: set[str] = set()

        for child_fingerprint in child_fingerprints:
            parents = self._parents.get(child_fingerprint)
            if not parents or parent_fingerprint not in parents:
                continue

            parents.discard(parent_fingerprint)
            if parents:
                continue

            self._parents.pop(child_fingerprint, None)
            if indicator := self.indicators.pop(child_fingerprint, None):
                purge_names.add(indicator.name)

        return purge_names

    def __contains__(self, fingerprint: str) -> bool:
        return fingerprint in self.indicators


indicator_registry: IndicatorRegistry = IndicatorRegistry()


def clear_registry() -> None:
    """Reset the global registry. Intended for tests."""
    indicator_registry.indicators.clear()
    indicator_registry.indicator_references.clear()
    indicator_registry._parents.clear()
