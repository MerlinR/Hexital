from typing import List, Union

from hexital.types.ohlcv import OHLCV
from hexital.utilities.ohlcv import (
    indicator_by_candle,
    indicator_by_index,
    indicator_period,
)


def positive(candles: Union[OHLCV, List[OHLCV]], posisiton: int = -1) -> bool:
    if isinstance(candles, list):
        return candles[posisiton].open < candles[posisiton].close
    return candles.open < candles.close


def negative(candles: Union[OHLCV, List[OHLCV]], posisiton: int = -1) -> bool:
    if isinstance(candles, list):
        return candles[posisiton].open > candles[posisiton].close
    return candles.open > candles.close


def basic_rising(candles: List[OHLCV], indicator: str, length: int = 1) -> bool:
    """True if current `indicator` is greater than any previous `indicator`
    for `length` bars back, False otherwise."""
    if not indicator_period(candles, length, indicator):
        return False

    newest = indicator_by_candle(candles[-1], indicator)
    return not any(
        val > newest
        for val in [
            indicator_by_candle(candle, indicator) for candle in candles[length * -1 : -1]
        ]
    )


def basic_falling(candles: List[OHLCV], indicator: str, length: int = 1) -> bool:
    """True if current `indicator` value is less than any previous `indicator`
    value for `length` bars back, False otherwise."""
    if not indicator_period(candles, length, indicator):
        return False

    newest = indicator_by_candle(candles[-1], indicator)
    return any(
        val > newest
        for val in [
            indicator_by_candle(candle, indicator) for candle in candles[length * -1 : -1]
        ]
    )


def rising(candles: List[OHLCV], indicator: str, length: int = 1) -> bool:
    """True if current `indicator` is greater than the avg of the previous
    `length` `indicator` bars back, False otherwise.

    Calc:
        NewestCandle[indicator] > mean(Candles[newest] to Candles[length])"""
    if not indicator_period(candles, length, indicator):
        return False

    mean = (
        sum(
            indicator_by_candle(candle, indicator) for candle in candles[length * -1 : -1]
        )
        / length
    )
    return round(mean, 2) < indicator_by_candle(candles[-1], indicator)


def falling(candles: List[OHLCV], indicator: str, length: int = 1) -> bool:
    """True if current `indicator` is less than the avg of the previous
    `length` `indicator` bars back, False otherwise.

    Calc:
        NewestCandle[indicator] > mean(Candles[newest] to Candles[length])"""
    if not indicator_period(candles, length, indicator):
        return False

    mean = (
        sum(
            indicator_by_candle(candle, indicator) for candle in candles[length * -1 : -1]
        )
        / length
    )
    return round(mean, 2) > indicator_by_candle(candles[-1], indicator)


def highest(candles: List[OHLCV], indicator: str, length: int = 1) -> float:
    """Highest value for a given number of bars back.
    Returns:
        Highest value in the series.
    """
    if not indicator_period(candles, length, indicator):
        return False

    return max(
        indicator_by_candle(candles[candle], indicator)
        for candle in candles[length * -1 : -1]
    )


def lowest(candles: List[OHLCV], indicator: str, length: int = 1) -> float:
    """Lowest value for a given number of bars back.
    Returns:
        Lowest value in the series.
    """
    if not indicator_period(candles, length, indicator):
        return False

    return min(
        indicator_by_candle(candles[candle], indicator)
        for candle in candles[length * -1 : -1]
    )


def highestbars(candles: List[OHLCV], indicator: str, length: int = 1) -> int:
    """Highest value offset for a given number of bars back.
    Returns:
        Offset to the lowest bar
    """
    if not indicator_period(candles, length, indicator):
        return False

    high = None
    distance = 0

    for dist, index in enumerate(range(len(candles), len(candles) - length, -1)):
        current = indicator_by_index(candles, indicator, index)

        if high and high < current:
            high = current
            distance = dist + 1
        elif high is None:
            high = indicator_by_index(index, indicator)

    return distance


def lowestbars(candles: List[OHLCV], indicator: str, length: int = 1) -> int:
    """Lowest value offset for a given number of bars back.
    Returns:
        Offset to the lowest bar
    """
    if not indicator_period(candles, length, indicator):
        return False

    low = None
    distance = 0

    for dist, index in enumerate(range(len(candles), len(candles) - length, -1)):
        current = indicator_by_index(candles, indicator, index)

        if low and low > current:
            low = current
            distance = dist + 1
        elif low is None:
            low = indicator_by_index(index, indicator)

    return distance
