from __future__ import annotations


def edge(current: bool | None, previous: bool | None) -> bool:
    """True when ``current`` is true and ``previous`` was not."""
    return bool(current) and not bool(previous)


def falling_edge(current: bool | None, previous: bool | None) -> bool:
    """True when ``current`` is false and ``previous`` was true."""
    return not bool(current) and bool(previous)


def level_edge(level: bool | None, previous_level: bool | None) -> bool:
    """True on the bar a level condition becomes true."""
    return edge(level, previous_level)


def level_falling_edge(level: bool | None, previous_level: bool | None) -> bool:
    """True on the bar a level condition becomes false."""
    return falling_edge(level, previous_level)


def crossed_above(
    current: float | int | None,
    previous: float | int | None,
    level: float | int,
) -> bool:
    """True when ``current`` crosses up through ``level`` from ``previous``."""
    if current is None or previous is None:
        return False
    return current > level and previous <= level


def crossed_below(
    current: float | int | None,
    previous: float | int | None,
    level: float | int,
) -> bool:
    """True when ``current`` crosses down through ``level`` from ``previous``."""
    if current is None or previous is None:
        return False
    return current < level and previous >= level


def between_values(
    value: float | int | None,
    low: float | int,
    high: float | int,
) -> bool:
    """True when ``value`` is within ``low`` and ``high`` inclusive."""
    if value is None:
        return False
    return low <= value <= high


def all_of(*conditions: bool | None) -> bool:
    """True when every condition is explicitly ``True``."""
    if not conditions:
        return False
    return all(condition is True for condition in conditions)


def any_of(*conditions: bool | None) -> bool:
    """True when any condition is explicitly ``True``."""
    return any(condition is True for condition in conditions)


def none_of(*conditions: bool | None) -> bool:
    """True when no condition is explicitly ``True``."""
    return not any(condition is True for condition in conditions)
