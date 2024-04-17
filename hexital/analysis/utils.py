from typing import List, Optional

from hexital.core.candle import Candle


def realbody_avg(candles: List[Candle], length: int, index: Optional[int] = None) -> float:
    """Includes Current Candle"""
    if index is None:
        index = len(candles) - 1
    index += 1
    start_index = 0 if index - length < 0 else index - length

    return sum(candles[i].realbody for i in range(start_index, index)) / length


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


def high_low_avg(candles: List[Candle], length: int, index: Optional[int] = None) -> float:
    """Includes Current Candle"""
    if index is None:
        index = len(candles) - 1
    index += 1
    start_index = 0 if index - length < 0 else index - length

    return sum(candles[i].high_low for i in range(start_index, index)) / length


# Below are TA-lib globally used utils
# https://github.com/TA-Lib/ta-lib/blob/main/src/ta_common/ta_global.c


def candle_doji(candles: List[Candle], index: Optional[int] = None, length: int = 10) -> float:
    """real body is like doji's body when it's shorter than 10% the average of the 10 previous candles' high-low range"""
    if index is None:
        index = len(candles) - 1

    return 0.1 * high_low_avg(candles, length, index)


def shadow_very_short(
    candles: List[Candle], index: Optional[int] = None, length: int = 10
) -> float:
    if index is None:
        index = len(candles) - 1

    return high_low_avg(candles, length, index) * 0.1


def candle_near(candles: List[Candle], index: Optional[int] = None, length: int = 5) -> float:
    if index is None:
        index = len(candles) - 1

    return high_low_avg(candles, length, index) * 0.2
