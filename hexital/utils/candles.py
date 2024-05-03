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

    for point in [
        period,
        period / 2,
        0,
    ]:
        if (
            reading_by_index(
                candles,
                name,
                index - int(point),
            )
            is None
        ):
            return False
    return True


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

    return sum(value for value in values if value is not None)
