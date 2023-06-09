from typing import List, Union

from hexital.types.ohlcv import OHLCV
from hexital.utilities.ohlcv import (
    indicator_by_candle,
    indicator_by_index,
    indicator_period,
)


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
    if not indicator_period(candles, length, indicator):
        length = len(candles)

    newest_candle = indicator_by_candle(candles[-1], indicator)

    return all(
        val < newest_candle
        for val in [
            indicator_by_candle(candle, indicator)
            for candle in candles[(length + 1) * -1 : -1]
        ]
    )


def basic_falling(candles: List[OHLCV], indicator: str, length: int = 4) -> bool:
    """True if current `indicator` value is less than any previous `indicator`
    value for `length` bars back, False otherwise. Length excludes latest"""
    if not indicator_period(candles, length, indicator):
        length = len(candles)

    newest_candle = indicator_by_candle(candles[-1], indicator)

    return any(
        val > newest_candle
        for val in [
            indicator_by_candle(candle, indicator)
            for candle in candles[(length + 1) * -1 : -1]
        ]
    )


def rising(candles: List[OHLCV], indicator: str, length: int = 4) -> bool:
    """True if current `indicator` is greater than the avg of the previous
    `length` `indicator` bars back, False otherwise. Length excludes latest

    Calc:
        NewestCandle[indicator] > mean(Candles[newest] to Candles[length])"""
    if not indicator_period(candles, length, indicator):
        length = len(candles)

    mean = (
        sum(
            indicator_by_candle(candle, indicator)
            for candle in candles[(length + 1) * -1 : -1]
        )
        / length
    )
    return round(mean, 2) < indicator_by_candle(candles[-1], indicator)


def falling(candles: List[OHLCV], indicator: str, length: int = 4) -> bool:
    """True if current `indicator` is less than the avg of the previous
    `length` `indicator` bars back, False otherwise. Length excludes latest

    Calc:
        NewestCandle[indicator] > mean(Candles[newest] to Candles[length])"""
    if not indicator_period(candles, length, indicator):
        length = len(candles)

    mean = (
        sum(
            indicator_by_candle(candle, indicator)
            for candle in candles[(length + 1) * -1 : -1]
        )
        / length
    )
    return round(mean, 2) > indicator_by_candle(candles[-1], indicator)


def highest(candles: List[OHLCV], indicator: str, length: int = 4) -> float:
    """Highest value for a given number of bars back. Includes latest.
    Returns:
        Highest value in the series.
    """
    if not indicator_period(candles, length, indicator):
        length = len(candles)

    return max(
        indicator_by_candle(candle, indicator) for candle in candles[length * -1 :]
    )


def lowest(candles: List[OHLCV], indicator: str, length: int = 4) -> float:
    """Lowest value for a given number of bars back. Includes latest.
    Returns:
        Lowest value in the series.
    """
    if not indicator_period(candles, length, indicator):
        length = len(candles)

    return min(
        indicator_by_candle(candle, indicator) for candle in candles[length * -1 :]
    )


def highestbars(candles: List[OHLCV], indicator: str, length: int = 4) -> int:
    """Highest value offset for a given number of bars back. Excludes latest.
    Returns:
        Offset to the lowest bar
    """
    if not indicator_period(candles, length, indicator):
        length = len(candles)

    high = None
    distance = 0
    start_index = len(candles) - 2

    for dist, index in enumerate(range(start_index, start_index - length, -1)):
        current = indicator_by_index(candles, indicator, index)

        if high and high < current:
            high = current
            distance = dist
        elif high is None:
            high = current

    return distance + 1


def lowestbars(candles: List[OHLCV], indicator: str, length: int = 4) -> int:
    """Lowest value offset for a given number of bars back. Excludes latest.
    Returns:
        Offset to the lowest bar
    """
    if not indicator_period(candles, length, indicator):
        length = len(candles)

    low = None
    distance = 0
    start_index = len(candles) - 2

    for dist, index in enumerate(range(start_index, start_index - length, -1)):
        current = indicator_by_index(candles, indicator, index)

        if low and low > current:
            low = current
            distance = dist
        elif low is None:
            low = current

    return distance + 1
