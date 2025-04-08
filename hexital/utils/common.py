from enum import Enum, auto
from typing import Any, Dict


class CalcMode(Enum):
    INSERT = auto()
    APPEND = auto()
    PREPEND = auto()


def round_values(
    value: float | Dict[str, float | None] | Any | None, round_by: int | None = 4
) -> float | Dict[str, float | None] | None:
    if round_by is None:
        return value

    if isinstance(value, float):
        return round(value, round_by)

    if isinstance(value, dict):
        for key, val in value.items():
            if isinstance(val, float):
                value[key] = round(val, round_by)

    return value
