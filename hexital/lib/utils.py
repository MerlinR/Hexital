from typing import Dict, Optional


def validate_index(index: Optional[int], length: int, default: int = -1) -> int | None:
    if index is None:
        index = default
    if not valid_index(index, length):
        return None
    return index


def absindex(index: int, length: int) -> int | None:
    """Ensure's Index is a positive index, -1 == length-1"""
    if index is None:
        return length - 1
    if not valid_index(index, length):
        return None
    if index < 0:
        return length + index
    return index


def valid_index(index: int, length: int) -> bool:
    if index is None:
        return False
    if not length > index >= -length:
        return False
    return True


def round_values(
    value: float | Dict[str, float | None] | None, round_by: int = 4
) -> float | Dict[str, float | None] | None:
    if isinstance(value, float):
        return round(value, round_by)

    if isinstance(value, dict):
        for key, val in value.items():
            if isinstance(val, float):
                value[key] = round(val, round_by)

    return value
