from itertools import chain
from typing import List, Optional

from hexital.types.ohlcv import OHLCV


def reading_by_index(
    candles: List[OHLCV], name: str, index: int = -1
) -> float | dict | None:
    """Simple method to get a reading from the given indicator from it's index"""
    return reading_by_candle(candles[index], name)


def reading_by_candle(candle: OHLCV, name: str) -> float | dict | None:
    """Simple method to get a reading from the given indicator from a candle
    Uses '.' to find nested reading, E.G 'MACD_12_26_9.MACD"""

    if "." in name:
        main_name, nested_name = name.split(".")
        reading = _nested_indicator(candle, main_name, nested_name)
        if reading:
            return reading

    if getattr(candle, name, None) is not None:
        return getattr(candle, name)

    if name in candle.indicators:
        return candle.indicators[name]

    if name in candle.sub_indicators:
        return candle.sub_indicators[name]

    for key, reading in chain(candle.indicators.items(), candle.sub_indicators.items()):
        if name in key:
            return reading

    return None


def _nested_indicator(candle: OHLCV, name: str, nested_name: str) -> float | None:
    if name in candle.indicators:
        if isinstance(candle.indicators[name], dict):
            return candle.indicators[name].get(nested_name)
        return candle.indicators[name]

    if name in candle.sub_indicators:
        if isinstance(candle.sub_indicators[name], dict):
            return candle.sub_indicators[name].get(nested_name)
        return candle.sub_indicators[name]

    for key, reading in chain(candle.indicators.items(), candle.sub_indicators.items()):
        if name in key:
            if isinstance(reading, dict):
                return reading.get(nested_name)
            return reading
    return None


def reading_count(candles: List[OHLCV], name: str) -> int:
    """Returns how many instance of the given indicator exist"""
    count = 0
    for candle in reversed(candles):
        if not reading_by_candle(candle, name):
            return count
        count += 1

    return count


def reading_as_list(candles: List[OHLCV], name: str) -> List[float | dict]:
    """Gathers the indicator for all candles as a list"""
    return [candle.indicators.get(name) for candle in candles]


def reading_period(
    candles: List[OHLCV], period: int, name: str, index: Optional[int] = None
) -> bool:
    """Will return True if the given indicator goes back as far as amount,
    It's true if exactly or more than. Period will be period-1"""
    if index is None:
        index = len(candles) - 1

    period -= 1

    if (index - period) < 0:
        return False

    # Checks 3 points along period to verify values exist
    return all(
        reading_by_index(
            candles,
            name,
            index - int(point),
        )
        for point in [
            period,
            period / 2,
            0,
        ]
    )
