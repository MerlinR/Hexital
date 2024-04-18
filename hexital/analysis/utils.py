from typing import List, Optional

from hexital.core.candle import Candle


def realbody_avg(candles: List[Candle], length: int, index: Optional[int] = None) -> float:
    """Includes Current Candle"""
    if index is None:
        index = len(candles) - 1
    index += 1
    start_index = 0 if index - length < 0 else index - length

    return sum(candles[i].realbody for i in range(start_index, index)) / length


def high_low_avg(candles: List[Candle], length: int, index: Optional[int] = None) -> float:
    """Includes Current Candle"""
    if index is None:
        index = len(candles) - 1
    index += 1
    start_index = 0 if index - length < 0 else index - length

    return sum(candles[i].high_low for i in range(start_index, index)) / length


def shadow_upper_avg(candles: List[Candle], length: int, index: Optional[int] = None) -> float:
    """Includes Current Candle"""
    if index is None:
        index = len(candles) - 1
    index += 1
    start_index = 0 if index - length < 0 else index - length

    return sum(candles[i].shadow_upper for i in range(start_index, index)) / length


def shadow_lower_avg(candles: List[Candle], length: int, index: Optional[int] = None) -> float:
    """Includes Current Candle"""
    if index is None:
        index = len(candles) - 1
    index += 1
    start_index = 0 if index - length < 0 else index - length

    return sum(candles[i].shadow_lower for i in range(start_index, index)) / length


def realbody_gapup(candle: Candle, candle_two: Candle) -> bool:
    return min(candle.open, candle.close) > max(candle_two.open, candle_two.close)


def realbody_gapdown(candle: Candle, candle_two: Candle) -> bool:
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
    """real body is like doji's body when it's shorter than 10% the average of the 10 previous candles' high-low range"""
    if index is None:
        index = len(candles) - 1

    return realbody_avg(candles, length, index) * percentage


def _high_low_percentage(
    candles: List[Candle], index: Optional[int] = None, percentage: float = 1.0, length: int = 10
) -> float:
    """real body is like doji's body when it's shorter than 10% the average of the 10 previous candles' high-low range"""
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
    """real body is long when it's longer than the average of the 10 previous candles' real body"""
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
        index = len(candles) - 1

    return candles[index].realbody


def candle_shadow_verylong(candles: List[Candle], index: Optional[int] = None) -> float:
    """shadow is very long when it's longer than 2 times the real body"""
    if index is None:
        index = len(candles) - 1

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
