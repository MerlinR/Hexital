from datetime import timedelta
from typing import List, Optional

from hexital.core.candle import Candle
from hexital.utils.indexing import absindex, valid_index
from hexital.utils.timeframe import round_down_timestamp


def reading_by_index(candles: List[Candle], name: str, index: int = -1) -> float | dict | None:
    """Simple method to get a reading from the given indicator from it's index"""
    if not valid_index(index, len(candles)):
        return None

    return reading_by_candle(candles[index], name)


def reading_by_candle(candle: Candle, name: str) -> float | dict | None:
    """Simple method to get a reading from the given indicator from a candle
    Uses '.' to find nested reading, E.G 'MACD_12_26_9.MACD"""

    if "." in name:
        main_name, nested_name = name.split(".")
        reading = _nested_indicator(candle, main_name, nested_name)
        return reading

    attr = getattr(candle, name, None)

    if attr is not None:
        return attr

    for key in candle.indicators:
        if key == name:
            return candle.indicators[key]

    for key in candle.sub_indicators:
        if key == name:
            return candle.sub_indicators[key]

    return None


def _nested_indicator(candle: Candle, name: str, nested_name: str) -> float | None:
    for key in candle.indicators:
        if key == name:
            reading = candle.indicators[key]
            return reading.get(nested_name) if isinstance(reading, dict) else reading

    for key in candle.sub_indicators:
        if key == name:
            reading = candle.sub_indicators[key]
            return reading.get(nested_name) if isinstance(reading, dict) else reading

    return None


def reading_count(candles: List[Candle], name: str) -> int:
    """Returns how many instance of the given indicator exist"""
    for count, candle in enumerate(reversed(candles)):
        if reading_by_candle(candle, name) is None:
            return count

    return len(candles)


def reading_period(
    candles: List[Candle], period: int, name: str, index: Optional[int] = None
) -> bool:
    """Will return True if the given indicator goes back as far as amount,
    It's true if exactly or more than. Will ignore latest Candle"""
    period -= 1

    if index is None:
        index = len(candles) - 1
    elif not valid_index(index, len(candles)):
        return False

    if index - period < 0:
        return False

    for point in [period, period / 2, 0]:
        if reading_by_index(candles, name, index - int(point)) is None:
            return False
    return True


def candles_sum(
    candles: List[Candle], indicator: str, length: int, index: int = -1
) -> float | None:
    """Sum of `indicator` for `length` bars back. including index/latest"""
    return sum(get_readings_period(candles, indicator, length, index, True))


def get_readings_period(
    candles: List[Candle], indicator: str, length: int, index: int, include_latest: bool = False
) -> List[float | int]:
    """Goes through from index-length to index and returns a list of values, removes dict's and None values
    Returns from newest at the back (same order)"""
    index_ = absindex(index, len(candles))
    index_ = len(candles) - 1 if index_ is None else index_

    to_index = index_ + 1 if include_latest else index_

    start = to_index - length
    start = 0 if start < 0 else start

    candles_ = []

    for candle in candles[start:to_index]:
        reading = reading_by_candle(candle, indicator)
        if isinstance(reading, (float, int)):
            candles_.append(reading)

    return candles_


def get_candles_period(
    candles: List[Candle], length: int, index: int, include_latest: bool = False
) -> List[Candle]:
    """Goes through from index-length to index and returns a list of values
    Returns from newest at the back (same order)"""
    index_ = absindex(index, len(candles))
    index_ = len(candles) - 1 if index_ is None else index_

    to_index = index_ + 1 if include_latest else index_

    start = to_index - length
    start = 0 if start < 0 else start

    return candles[start:to_index]


def get_readings_timeframe(
    candles: List[Candle],
    indicator: str,
    timeframe: timedelta,
    index: int,
    include_latest: bool = False,
    rounded_timeframe: bool = False,
) -> List[float | int]:
    """Goes through from index and returns readings that are less or equal to timeframe to index candle
    removes dict's and None values
    Returns from newest at the back (same order)"""
    index_ = absindex(index, len(candles))
    index_ = len(candles) - 1 if index_ is None else index_

    to_index = index_ if include_latest else index_ - 1

    if rounded_timeframe:
        index_timestamp = round_down_timestamp(candles[index_].timestamp, timeframe) + timeframe
    else:
        index_timestamp = candles[index_].timestamp

    candles_ = []

    for candle in candles[to_index::-1]:
        if (index_timestamp - candle.timestamp) > timeframe:
            break
        reading = reading_by_candle(candle, indicator)
        if isinstance(reading, (float, int)):
            candles_.insert(0, reading)

    return candles_


def get_candles_timeframe(
    candles: List[Candle],
    timeframe: timedelta,
    index: int,
    include_latest: bool = False,
    rounded_timeframe: bool = False,
) -> List[Candle]:
    """Goes through from index and returns candles that are less or equal to timeframe to index candle
    Returns from newest at the back (same order)"""
    index_ = absindex(index, len(candles))
    index_ = len(candles) - 1 if index_ is None else index_

    to_index = index_ if include_latest else index_ - 1

    if rounded_timeframe:
        index_timestamp = round_down_timestamp(candles[index_].timestamp, timeframe) + timeframe
    else:
        index_timestamp = candles[index_].timestamp

    candles_ = []

    for candle in candles[to_index::-1]:
        if (index_timestamp - candle.timestamp) > timeframe:
            break
        candles_.insert(0, candle)

    return candles_
