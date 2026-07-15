from __future__ import annotations

from datetime import timedelta
from typing import Any

from .timeframe import convert_timeframe_to_timedelta

DURATION_KEYS = frozenset({"candle_life"})


def decode_settings(value: Any) -> Any:
    """Restore duration fields from external settings (e.g. after JSON load)."""
    if isinstance(value, dict):
        decoded: dict[str, Any] = {}
        for key, item in value.items():
            if key in DURATION_KEYS:
                decoded[key] = _decode_duration(item)
            else:
                decoded[key] = decode_settings(item)
        return decoded
    if isinstance(value, list):
        return [decode_settings(item) for item in value]
    return value


def _decode_duration(value: Any) -> timedelta | None:
    if value is None:
        return None
    if isinstance(value, timedelta):
        return value
    if isinstance(value, str):
        return convert_timeframe_to_timedelta(value)
    if isinstance(value, (int, float)):
        return timedelta(seconds=value)
    raise ValueError(f"Invalid duration value: {value!r}")
