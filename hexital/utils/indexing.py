from typing import Dict


def absindex(index: int | None, length: int) -> int:
    """Ensure's Index is a positive index, -1 == length-1"""
    if index is None:
        return length - 1
    if not valid_index(index, length):
        return length - 1
    if index < 0:
        return length + index
    return index


def valid_index(index: int | None, length: int) -> bool:
    if index is None:
        return False
    if not length > index >= -length:
        return False
    return True


def round_values(
    value: float | Dict[str, float | None] | None, round_by: int | None = 4
) -> float | Dict[str, float | None] | None:
    if not round_by:
        return value

    if isinstance(value, float):
        return round(value, round_by)

    if isinstance(value, dict):
        for key, val in value.items():
            if isinstance(val, float):
                value[key] = round(val, round_by)

    return value
