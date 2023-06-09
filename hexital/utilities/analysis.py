from typing import List, Union

from hexital.types.ohlcv import OHLCV
from hexital.utilities.ohlcv import reading_by_candle, reading_by_index, reading_period


def positive(candles: Union[OHLCV, List[OHLCV]], position: int = -1) -> bool:
    if isinstance(candles, list):
        if position >= len(candles):
            position = -1
        return candles[position].open < candles[position].close
    return candles.open < candles.close


def negative(candles: Union[OHLCV, List[OHLCV]], position: int = -1) -> bool:
    if isinstance(candles, list):
        if position >= len(candles):
            position = -1
        return candles[position].open > candles[position].close
    return candles.open > candles.close


def basic_rising(candles: List[OHLCV], indicator: str, length: int = 4) -> bool:
    """True if current `indicator` is greater than any previous `indicator`
    for `length` bars back, False otherwise. Length excludes latest"""
    if not reading_period(candles, length, indicator):
        length = len(candles)

    newest_reading = reading_by_candle(candles[-1], indicator)

    return all(
        val < newest_reading
        for val in [
            reading_by_candle(candle, indicator)
            for candle in candles[(length + 1) * -1 : -1]
        ]
    )


def basic_falling(candles: List[OHLCV], indicator: str, length: int = 4) -> bool:
    """True if current `indicator` reading is less than any previous `indicator`
    reading for `length` bars back, False otherwise. Length excludes latest"""
    if not reading_period(candles, length, indicator):
        length = len(candles)

    newest_reading = reading_by_candle(candles[-1], indicator)

    return any(
        val > newest_reading
        for val in [
            reading_by_candle(candle, indicator)
            for candle in candles[(length + 1) * -1 : -1]
        ]
    )


def rising(candles: List[OHLCV], indicator: str, length: int = 4) -> bool:
    """True if current `indicator` reading is greater than the avg of the previous
    `length` `indicator` reading bars back, False otherwise. Length excludes latest

    Calc:
        NewestCandle[indicator] > mean(Candles[newest] to Candles[length])"""
    if not reading_period(candles, length, indicator):
        length = len(candles)

    mean = (
        sum(
            reading_by_candle(candle, indicator)
            for candle in candles[(length + 1) * -1 : -1]
        )
        / length
    )
    return round(mean, 2) < reading_by_candle(candles[-1], indicator)


def falling(candles: List[OHLCV], indicator: str, length: int = 4) -> bool:
    """True if current `indicator` is less than the avg of the previous
    `length` `indicator` bars back, False otherwise. Length excludes latest

    Calc:
        NewestCandle[indicator] > mean(Candles[newest] to Candles[length])"""
    if not reading_period(candles, length, indicator):
        length = len(candles)

    mean = (
        sum(
            reading_by_candle(candle, indicator)
            for candle in candles[(length + 1) * -1 : -1]
        )
        / length
    )
    return round(mean, 2) > reading_by_candle(candles[-1], indicator)


def highest(candles: List[OHLCV], indicator: str, length: int = 4) -> float:
    """Highest reading for a given number of bars back. Includes latest.
    Returns:
        Highest reading in the series.
    """
    if not reading_period(candles, length, indicator):
        length = len(candles)

    return max(reading_by_candle(candle, indicator) for candle in candles[length * -1 :])


def lowest(candles: List[OHLCV], indicator: str, length: int = 4) -> float:
    """Lowest reading for a given number of bars back. Includes latest.
    Returns:
        Lowest reading in the series.
    """
    if not reading_period(candles, length, indicator):
        length = len(candles)

    return min(reading_by_candle(candle, indicator) for candle in candles[length * -1 :])


def highestbars(candles: List[OHLCV], indicator: str, length: int = 4) -> int:
    """Highest reading offset for a given number of bars back. Excludes latest.
    Returns:
        Offset to the lowest bar
    """
    if not reading_period(candles, length, indicator):
        length = len(candles)

    high = None
    distance = 0
    start_index = len(candles) - 2

    for dist, index in enumerate(range(start_index, start_index - length, -1)):
        current = reading_by_index(candles, indicator, index)

        if high and high < current:
            high = current
            distance = dist
        elif high is None:
            high = current

    return distance + 1


def lowestbars(candles: List[OHLCV], indicator: str, length: int = 4) -> int:
    """Lowest reading offset for a given number of bars back. Excludes latest.
    Returns:
        Offset to the lowest bar
    """
    if not reading_period(candles, length, indicator):
        length = len(candles)

    low = None
    distance = 0
    start_index = len(candles) - 2

    for dist, index in enumerate(range(start_index, start_index - length, -1)):
        current = reading_by_index(candles, indicator, index)

        if low and low > current:
            low = current
            distance = dist
        elif low is None:
            low = current

    return distance + 1
