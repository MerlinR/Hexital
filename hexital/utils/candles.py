from typing import List, Optional

from hexital.core.candle import Candle
from hexital.utils.indexing import absindex, valid_index


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

    if name in candle.indicators:
        return candle.indicators[name]

    if name in candle.sub_indicators:
        return candle.sub_indicators[name]

    return None


def _nested_indicator(candle: Candle, name: str, nested_name: str) -> float | None:
    if name in candle.indicators:
        reading = candle.indicators[name]
        return reading.get(nested_name) if isinstance(reading, dict) else reading

    if name in candle.sub_indicators:
        reading = candle.sub_indicators[name]
        return reading.get(nested_name) if isinstance(reading, dict) else reading

    return None


def reading_count(candles: List[Candle], name: str, index: Optional[int] = None) -> int:
    """Returns how many instance of the given indicator exist"""
    index_ = absindex(index, len(candles))

    for count, idx in enumerate(range(index_, -1, -1)):
        if reading_by_candle(candles[idx], name) is None:
            return count

    return index_ + 1


def reading_period(
    candles: List[Candle], name: str, period: int, index: Optional[int] = None
) -> bool:
    """Will return True if the given indicator goes back as far as amount,
    It's true if exactly or more than. Includes index"""
    if not candles:
        return False

    period_ = period - 1
    index_ = absindex(index, len(candles))

    if index_ - period_ < 0:
        return False

    for point in [period_, period_ / 2, 0]:
        if reading_by_index(candles, name, index_ - int(point)) is None:
            return False
    return True


def candles_sum(
    candles: List[Candle],
    name: str,
    length: int,
    index: int = -1,
    include_latest: bool = True,
) -> float:
    """Sum of `name` for `length` bars back. If not enough Candles, sum's what's available"""
    return sum(get_readings_period(candles, name, length, index, include_latest))


def candles_average(
    candles: List[Candle],
    name: str,
    length: int,
    index: int = -1,
    include_latest: bool = True,
) -> float:
    """Averages period of `name` for `length` bars back.
    If not enough Candles, sum's what's available"""
    values = get_readings_period(candles, name, length, index, include_latest)
    return sum(values) / len(values) if values else 0


def get_readings_period(
    candles: List[Candle], name: str, length: int, index: int, include_latest: bool = False
) -> List[float | int]:
    """Goes through from index-length to index and returns a list of values, removes dict's and None values, validates index, if out of range set to max (-1)
    Returns from newest at the back (same order)"""
    index_ = absindex(index, len(candles))

    to_index = index_ + 1 if include_latest else index_

    start = to_index - length
    start = 0 if start < 0 else start

    readings = []

    for candle in candles[start:to_index]:
        reading = reading_by_candle(candle, name)
        if isinstance(reading, (float, int)):
            readings.append(reading)

    return readings
