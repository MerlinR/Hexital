from __future__ import annotations

from enum import Enum

from ...exceptions import InvalidIndicator


class ChildWhen(str, Enum):
    """When a child indicator is calculated relative to its parent."""

    BEFORE = "before"
    AFTER = "after"
    MANUAL = "manual"


def _normalize_when(when: ChildWhen | str) -> ChildWhen:
    if isinstance(when, ChildWhen):
        return when
    try:
        return ChildWhen(when)
    except ValueError as exc:
        raise InvalidIndicator(
            f"Invalid child when {when!r}; expected one of "
            f"{', '.join(member.value for member in ChildWhen)}"
        ) from exc
