from typing import List, Union

from hexital.core.candle import Candle
from hexital.lib.candle_extension import (
    reading_by_candle,
    reading_by_index,
    reading_count,
    reading_period,
)


def positive(candles: Union[Candle, List[Candle]], position: int = -1) -> bool:
    if isinstance(candles, list):
        if position >= len(candles):
            position = -1
        return candles[position].open < candles[position].close
    return candles.open < candles.close


def negative(candles: Union[Candle, List[Candle]], position: int = -1) -> bool:
    if isinstance(candles, list):
        if position >= len(candles):
            position = -1
        return candles[position].open > candles[position].close
    return candles.open > candles.close


def value_range(candles: List[Candle], indicator: str, length: int = 4) -> bool:
    """Returns the difference between the min and max values in a indicator series.
    Length `includes` latest"""
    if not reading_period(candles, length, indicator):
        length = reading_count(candles, indicator)

    readings = [
        reading_by_candle(candle, indicator)
        for candle in candles[-abs(length + 1) : len(candles)]
    ]

    return abs(min(readings) - max(readings))


def rising(candles: List[Candle], indicator: str, length: int = 4) -> bool:
    """True if current `indicator` is greater than any previous `indicator`
    for `length` bars back, False otherwise.
    Length `excludes` latest"""
    if not reading_period(candles, length, indicator):
        length = reading_count(candles, indicator)

    newest_reading = reading_by_candle(candles[-1], indicator)

    return all(
        val < newest_reading
        for val in [
            reading_by_candle(candle, indicator)
            for candle in candles[-abs(length + 1) : -1]
        ]
    )


def falling(candles: List[Candle], indicator: str, length: int = 4) -> bool:
    """True if current `indicator` reading is less than any previous `indicator`
    reading for `length` bars back, False otherwise.
    Length `excludes` latest"""
    if not reading_period(candles, length, indicator):
        length = reading_count(candles, indicator)

    newest_reading = reading_by_candle(candles[-1], indicator)

    return any(
        val > newest_reading
        for val in [
            reading_by_candle(candle, indicator)
            for candle in candles[-abs(length + 1) : -1]
        ]
    )


def mean_rising(candles: List[Candle], indicator: str, length: int = 4) -> bool:
    """True if current `indicator` reading is greater than the avg of the previous
    `length` `indicator` reading bars back, False otherwise. Length `excludes` latest

    Calc:
        NewestCandle[indicator] > mean(Candles[newest] to Candles[length])"""
    if not reading_period(candles, length, indicator):
        length = reading_count(candles, indicator)

    mean = (
        sum(
            reading_by_candle(candle, indicator)
            for candle in candles[-abs(length + 1) : -1]
        )
        / length
    )
    return round(mean, 2) < reading_by_candle(candles[-1], indicator)


def mean_falling(candles: List[Candle], indicator: str, length: int = 4) -> bool:
    """True if current `indicator` is less than the avg of the previous
    `length` `indicator` bars back, False otherwise. Length `excludes` latest

    Calc:
        NewestCandle[indicator] > mean(Candles[newest] to Candles[length])"""
    if not reading_period(candles, length, indicator):
        length = reading_count(candles, indicator)

    mean = (
        sum(
            reading_by_candle(candle, indicator)
            for candle in candles[-abs(length + 1) : -1]
        )
        / length
    )
    return round(mean, 2) > reading_by_candle(candles[-1], indicator)


def highest(candles: List[Candle], indicator: str, length: int = 4) -> float:
    """Highest reading for a given number of bars back. Length `Includes` latest.
    Returns:
        Highest reading in the series.
    """
    if not reading_period(candles, length, indicator):
        length = reading_count(candles, indicator)

    return max(reading_by_candle(candle, indicator) for candle in candles[-abs(length) :])


def lowest(candles: List[Candle], indicator: str, length: int = 4) -> float:
    """Lowest reading for a given number of bars back. Length `Includes` latest.
    Returns:
        Lowest reading in the series.
    """
    if not reading_period(candles, length, indicator):
        length = reading_count(candles, indicator)

    return min(reading_by_candle(candle, indicator) for candle in candles[-abs(length) :])


def highestbar(candles: List[Candle], indicator: str, length: int = 4) -> int:
    """Highest reading offset for a given number of bars back. Length `Excludes` latest.
    Returns:
        Offset to the lowest bar
    """
    if not reading_period(candles, length, indicator):
        length = reading_count(candles, indicator)

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


def lowestbar(candles: List[Candle], indicator: str, length: int = 4) -> int:
    """Lowest reading offset for a given number of bars back. Length `Excludes` latest.
    Returns:
        Offset to the lowest bar
    """
    if not reading_period(candles, length, indicator):
        length = reading_count(candles, indicator)

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


def cross(
    candles: List[Candle], indicator_one: str, indicator_two: str, length: int = 1
) -> bool:
    """The `indicator_one` reading is defined as having crossed `indicator_two` reading"""
    if not reading_period(candles, length, indicator_one) or not reading_period(
        candles, length, indicator_two
    ):
        length = min(
            [reading_count(candles, indicator_one), reading_count(candles, indicator_two)]
        )

    over = reading_by_index(candles, indicator_one) > reading_by_index(
        candles, indicator_two
    )

    start_index = len(candles) - 2

    for index in range(start_index, start_index - length, -1):
        if (
            reading_by_index(candles, indicator_one, index)
            > reading_by_index(candles, indicator_two, index)
        ) != over:
            return True

    return False


def crossover(
    candles: List[Candle], indicator_one: str, indicator_two: str, length: int = 1
) -> bool:
    """The `indicator_one` reading is defined as having crossed over `indicator_two` reading,
    If  `indicator_two` is higher then `indicator_one` and in the last `length` it was under"""
    if not reading_period(candles, length, indicator_one) or not reading_period(
        candles, length, indicator_two
    ):
        length = min(
            [reading_count(candles, indicator_one), reading_count(candles, indicator_two)]
        )

    if not reading_by_index(candles, indicator_one) > reading_by_index(
        candles, indicator_two
    ):
        return False

    start_index = len(candles) - 2

    for index in range(start_index, start_index - length, -1):
        if reading_by_index(candles, indicator_one, index) < reading_by_index(
            candles, indicator_two, index
        ):
            return True

    return False


def crossunder(
    candles: List[Candle], indicator_one: str, indicator_two: str, length: int = 1
) -> bool:
    """The `indicator_one` reading is defined as having crossed under `indicator_two` reading,
    If  `indicator_two` is lower then `indicator_one` and in the last `length` it was over"""
    if not reading_period(candles, length, indicator_one) or not reading_period(
        candles, length, indicator_two
    ):
        length = min(
            [reading_count(candles, indicator_one), reading_count(candles, indicator_two)]
        )

    if not reading_by_index(candles, indicator_one) < reading_by_index(
        candles, indicator_two
    ):
        return False

    start_index = len(candles) - 2

    for index in range(start_index, start_index - length, -1):
        if reading_by_index(candles, indicator_one, index) > reading_by_index(
            candles, indicator_two, index
        ):
            return True

    return False
