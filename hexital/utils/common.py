from dataclasses import dataclass
from math import fabs, sqrt
from sys import float_info
from enum import Enum, auto
from typing import Sequence, TypeVar, cast


class CalcMode(Enum):
    INSERT = auto()
    APPEND = auto()
    PREPEND = auto()


T = TypeVar("T")


@dataclass(frozen=True)
class LinearRegressionStats:
    slope: float
    intercept: float
    line: float
    residual_stdev: float


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


def linear_regression_stats(values: Sequence[float]) -> LinearRegressionStats:
    period = len(values)
    x_sum = 0.5 * period * (period + 1)
    x2_sum = x_sum * (2 * period + 1) / 3
    divisor = period * x2_sum - x_sum * x_sum

    y_sum = sum(values)
    xy_sum = sum(x * y for x, y in enumerate(values, start=1))

    slope = (period * xy_sum - x_sum * y_sum) / divisor
    intercept = (y_sum * x2_sum - x_sum * xy_sum) / divisor
    line = (slope * (period - 1)) + intercept

    residual_sum = 0.0
    for x, y in enumerate(values, start=1):
        fitted = (slope * x) + intercept
        residual_sum += (y - fitted) ** 2

    residual_stdev = sqrt(residual_sum / period)
    return LinearRegressionStats(
        slope=slope,
        intercept=intercept,
        line=line,
        residual_stdev=residual_stdev,
    )
