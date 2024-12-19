from typing import List, Optional

from hexital.core.candle import Candle
from hexital.utils.candles import get_readings_period


def highest(
    candles: List[Candle], indicator: str, length: int, index: Optional[int] = None
) -> float | None:
    """
    Computes the highest value of the specified `indicator` over a given range of candles.
    The range includes the latest candle by default and considers up to the specified number of candles.
    """
    if index is None:
        index = len(candles) - 1

    readings = get_readings_period(candles, indicator, length, index, True)
    return max(readings, default=None)


def lowest(
    candles: List[Candle], indicator: str, length: int, index: Optional[int] = None
) -> float | None:
    """
    Computes the lowest value of the specified `indicator` over a given range of candles.
    The range includes the latest candle by default and considers up to the specified number of candles.
    """

    if not candles:
        return None
    if index is None:
        index = len(candles) - 1

    readings = get_readings_period(candles, indicator, length, index, True)
    return min(readings, default=None)


def realbody_avg(candles: List[Candle], length: int, index: Optional[int] = None) -> float:
    """
    Computes the average real body of a specified number of candles, including the current candle.
    The real body is calculated as the absolute difference between a candle's open and close prices.
    """

    if index is None:
        index = len(candles) - 1
    index += 1
    start_index = 0 if index - length < 0 else index - length

    return sum(candles[i].realbody for i in range(start_index, index)) / length


def high_low_avg(candles: List[Candle], length: int, index: Optional[int] = None) -> float:
    """
    Computes the average of the high-low range over a specified number of candles,
    including the current candle. The high-low range is the difference between a candle's
    high and low prices.
    """

    if index is None:
        index = len(candles) - 1
    index += 1
    start_index = 0 if index - length < 0 else index - length

    return sum(candles[i].high_low for i in range(start_index, index)) / length


def shadow_upper_avg(candles: List[Candle], length: int, index: Optional[int] = None) -> float:
    """
    Computes the average upper shadow over a specified number of candles, including the current candle.
    The upper shadow is the difference between a candle's high price and either its open or close price.
    """
    if index is None:
        index = len(candles) - 1
    index += 1
    start_index = 0 if index - length < 0 else index - length

    return sum(candles[i].shadow_upper for i in range(start_index, index)) / length


def shadow_lower_avg(candles: List[Candle], length: int, index: Optional[int] = None) -> float:
    """
    Computes the average lower shadow over a specified number of candles, including the current candle.
    The lower shadow is the difference between a candle's high price and either its open or close price.
    """
    if index is None:
        index = len(candles) - 1
    index += 1
    start_index = 0 if index - length < 0 else index - length

    return sum(candles[i].shadow_lower for i in range(start_index, index)) / length


def realbody_gapup(candle: Candle, candle_two: Candle) -> bool:
    """
    Computes if a candle has a real body gap-up compared to a previous candle.
    A gap-up occurs when the minimum value of the current candle's real body
    (i.e., the lower of its open or close) is greater than the maximum value
    of the previous candle's real body (i.e., the higher of its open or close).
    """

    return min(candle.open, candle.close) > max(candle_two.open, candle_two.close)


def realbody_gapdown(candle: Candle, candle_two: Candle) -> bool:
    """
    Computes if a candle has a real body gap-down compared to a previous candle.
    A gap-down occurs when the maximum value of the current candle's real body
    (i.e., the higher of its open or close) is less than the minimum value
    of the previous candle's real body (i.e., the lower of its open or close).
    """

    return max(candle.open, candle.close) < min(candle_two.open, candle_two.close)


def candle_gapup(candle: Candle, candle_two: Candle) -> bool:
    return candle.low > candle_two.high


def candle_gapdown(candle: Candle, candle_two: Candle) -> bool:
    return candle.high < candle_two.low


# Below are TA-lib globally used utils
# https://github.com/TA-Lib/ta-lib/blob/main/src/ta_common/ta_global.c


def _realbody_percentage(
    candles: List[Candle], index: Optional[int] = None, percentage: float = 1.0, length: int = 10
) -> float:
    if index is None:
        index = len(candles) - 1

    return realbody_avg(candles, length, index) * percentage


def _high_low_percentage(
    candles: List[Candle], index: Optional[int] = None, percentage: float = 1.0, length: int = 10
) -> float:
    if index is None:
        index = len(candles) - 1

    return high_low_avg(candles, length, index) * percentage


def candle_doji(candles: List[Candle], index: Optional[int] = None, length: int = 10) -> float:
    """real body is like doji's body when it's shorter than 10% the average of the 10 previous candles' high-low range"""
    return _high_low_percentage(candles, index=index, length=length, percentage=0.1)


def candle_bodylong(candles: List[Candle], index: Optional[int] = None, length: int = 10) -> float:
    """real body is long when it's longer than the average of the 10 previous candles' real body"""
    return _realbody_percentage(candles, index=index, length=length)


def candle_bodyverylong(
    candles: List[Candle], index: Optional[int] = None, length: int = 10
) -> float:
    """real body is very long when it's longer than 3 times the average of the 10 previous candles' real body"""
    return _realbody_percentage(candles, index=index, length=length, percentage=3)


def candle_bodyshort(
    candles: List[Candle], index: Optional[int] = None, length: int = 10
) -> float:
    """real body is short when it's shorter than the average of the 10 previous candles' real bodies"""
    return _realbody_percentage(candles, index=index, length=length)


def candle_shadow_veryshort(
    candles: List[Candle], index: Optional[int] = None, length: int = 10
) -> float:
    """shadow is very short when it's shorter than 10% the average of the 10 previous candles' high-low range"""
    return _high_low_percentage(candles, index=index, length=length, percentage=0.1)


def candle_shadow_short(
    candles: List[Candle], index: Optional[int] = None, length: int = 10
) -> float:
    """shadow is short when it's shorter than half the average of the 10 previous candles' sum of shadows"""
    return _high_low_percentage(candles, index=index, length=length)


def candle_shadow_long(candles: List[Candle], index: Optional[int] = None) -> float:
    """shadow is long when it's longer than the real body"""
    if index is None:
        index = -1

    return candles[index].realbody


def candle_shadow_verylong(candles: List[Candle], index: Optional[int] = None) -> float:
    """shadow is very long when it's longer than 2 times the real body"""
    if index is None:
        index = -1

    return candles[index].realbody * 2


def candle_near(candles: List[Candle], index: Optional[int] = None, length: int = 5) -> float:
    """when measuring distance between parts of candles or width of gaps
    near means "<= 20% of the average of the 5 previous candles' high-low range" """
    return _high_low_percentage(candles, index=index, length=length, percentage=0.2)


def candle_far(candles: List[Candle], index: Optional[int] = None, length: int = 5) -> float:
    """when measuring distance between parts of candles or width of gaps
    far means ">= 60% of the average of the 5 previous candles' high-low range"""
    return _high_low_percentage(candles, index=index, length=length, percentage=0.6)


def candle_equal(candles: List[Candle], index: Optional[int] = None, length: int = 5) -> float:
    """when measuring distance between parts of candles or width of gaps
    equal means "<= 5% of the average of the 5 previous candles' high-low range"""
    return _high_low_percentage(candles, index=index, length=length, percentage=0.05)
