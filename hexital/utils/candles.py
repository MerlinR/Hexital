from datetime import datetime
from typing import TypeAlias

from ..core.candle import Candle
from .indexing import absindex, valid_index

Candles: TypeAlias = Candle | list[Candle] | dict | list[dict] | list | list[list]


def parse_candles(candles: Candles) -> list[Candle]:
    candles_ = []

    if isinstance(candles, Candle):
        candles_.append(candles)
    elif isinstance(candles, dict):
        candles_.append(Candle.from_dict(candles))
    elif isinstance(candles, list) and candles:
        candle_ = candles[0]
        if isinstance(candle_, Candle):
            candles_.extend(candles)
        elif isinstance(candle_, dict):
            candles_.extend(Candle.from_dicts(candles))
        elif isinstance(candle_, (float, int, datetime)):
            candles_.append(Candle.from_list(candles))
        elif isinstance(candle_, list):
            candles_.extend(Candle.from_lists(candles))
        else:
            raise TypeError

    return candles_


def reading_by_index(
    candles: list[Candle], name: str, index: int = -1
) -> float | dict | None:
    """Simple method to get a reading from the given indicator from it's index"""
    if not valid_index(index, len(candles)):
        return None

    return reading_by_candle(candles[index], name)


def reading_by_candle(candle: Candle, name: str) -> float | dict | None:
    """Simple method to get a reading from the given indicator from a candle
    Uses '.' to find nested reading, E.G 'MACD_12_26_9.MACD"""

    if "." in name:
        main_name, nested_name = name.split(".")
        if (reading := candle.indicators.get(main_name)) is not None:
            return reading.get(nested_name) if isinstance(reading, dict) else reading

        if (reading := candle.sub_indicators.get(main_name)) is not None:
            return reading.get(nested_name) if isinstance(reading, dict) else reading

        return reading

    attr = getattr(candle, name, None)
    if attr is not None:
        return attr

    if (reading := candle.indicators.get(name)) is not None:
        return reading

    if (reading := candle.sub_indicators.get(name)) is not None:
        return reading

    return None


def reading_count(candles: list[Candle], name: str, index: int | None = None) -> int:
    """Returns how many instance of the given indicator exist"""
    index_ = absindex(index, len(candles))

    for count, idx in enumerate(range(index_, -1, -1)):
        if reading_by_candle(candles[idx], name) is None:
            return count

    return index_ + 1


def reading_period(
    candles: list[Candle], name: str, period: int, index: int | None = None
) -> bool:
    """Will return True if the given indicator goes back as far as amount,
    It's true if exactly or more than. Includes index"""
    if not candles:
        return False

    index_ = absindex(index, len(candles))
    oldest_index = index_ - (period - 1)

    if oldest_index < 0:
        return False

    return reading_by_index(candles, name, oldest_index) is not None


def candles_sum(
    candles: list[Candle],
    name: str,
    length: int,
    index: int = -1,
    include_latest: bool = True,
) -> float:
    """Sum of `name` for `length` bars back. If not enough Candles, sum's what's available"""
    return sum(get_readings_period(candles, name, length, index, include_latest))


def candles_average(
    candles: list[Candle],
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
    candles: list[Candle],
    name: str,
    length: int,
    index: int,
    include_latest: bool = False,
) -> list[float | int]:
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
