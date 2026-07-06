from math import fabs
from sys import float_info
from enum import Enum, auto
from typing import TypeVar, cast


class CalcMode(Enum):
    INSERT = auto()
    APPEND = auto()
    PREPEND = auto()


T = TypeVar("T")


def round_values(value: T, round_by: int | None = 4) -> T:
    if round_by is None:
        return value

    if isinstance(value, float):
        return cast(T, round(value, round_by))

    if isinstance(value, dict):
        # narrow to the expected mapping for assignment
        d = cast(dict[str, float | None], value)
        for key, val in d.items():
            if isinstance(val, float):
                d[key] = round(val, round_by)
        return cast(T, d)

    return value


def non_zero_range(value_a: float, value_b: float) -> float:
    difference = fabs(value_a - value_b)
    if difference == 0:
        return float_info.epsilon
    return difference
