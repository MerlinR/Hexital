from itertools import chain
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
        if reading is not None:
            return reading

    if getattr(candle, name, None) is not None:
        return getattr(candle, name)

    for key, reading in chain(candle.indicators.items(), candle.sub_indicators.items()):
        if name in key:
            return reading

    return None


def _nested_indicator(candle: Candle, name: str, nested_name: str) -> float | None:
    for key, reading in chain(candle.indicators.items(), candle.sub_indicators.items()):
        if name in key:
            return reading.get(nested_name) if isinstance(reading, dict) else reading

    return None


def reading_count(candles: List[Candle], name: str) -> int:
    """Returns how many instance of the given indicator exist"""
    for count, candle in enumerate(reversed(candles)):
        if not reading_by_candle(candle, name):
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

    return all(
        bool(
            reading_by_index(
                candles,
                name,
                index - int(point),
            )
            is not None
        )
        for point in [
            period,
            period / 2,
            0,
        ]
    )


def candles_sum(
    candles: List[Candle], indicator: str, length: int, index: int = -1
) -> float | None:
    """Sum of `indicator` for `length` bars back. including index/latest"""
    index_ = absindex(index, len(candles))
    if not index_:
        return

    index_ += 1

    length = len(candles) if length > len(candles) else length
    values = [reading_by_candle(candle, indicator) for candle in candles[index_ - length : index_]]

    return sum(value for value in values if value and isinstance(value, (int, float)))
