from typing import List, Union

from hexital.core.candle import Candle
from hexital.lib.candle_extension import (
    reading_by_candle,
    reading_by_index,
    reading_count,
    reading_period,
)
from hexital.lib.utils import absindex, valid_index


def positive(candles: Union[Candle, List[Candle]], position: int = -1) -> bool:
    if not candles:
        return False
    if isinstance(candles, list):
        if not valid_index(position, len(candles)):
            return False
        return candles[position].open < candles[position].close
    return candles.open < candles.close


def negative(candles: Union[Candle, List[Candle]], position: int = -1) -> bool:
    if not candles:
        return False
    if isinstance(candles, list):
        if not valid_index(position, len(candles)):
            return False
        return candles[position].open > candles[position].close
    return candles.open > candles.close


def value_range(candles: List[Candle], indicator: str, length: int = 4) -> float:
    """Returns the difference between the min and max values in a indicator series.
    Length `includes` latest, if lenth is too long for amount of candles,
    will check all of them"""
    end_index = absindex(-1, len(candles))
    if end_index is None:
        return None

    if not reading_period(candles, length, indicator):
        length = reading_count(candles, indicator) - 1

    if length < 2:
        return None

    readings = [
        reading_by_candle(candle, indicator)
        for candle in candles[end_index - length : end_index + 1]
    ]
    return abs(min(readings) - max(readings))


def rising(candles: List[Candle], indicator: str, length: int = 4) -> bool:
    """True if current `indicator` is greater than any previous `indicator`
    for `length` bars back, False otherwise.
    Length `excludes` latest"""
    end_index = absindex(-1, len(candles))
    if end_index is None:
        return False

    if not reading_period(candles, length, indicator):
        length = reading_count(candles, indicator) - 1

    if length < 1 or len(candles) < 2:
        return False

    newest_reading = reading_by_candle(candles[-1], indicator)

    return all(
        val < newest_reading
        for val in [
            reading_by_candle(candle, indicator)
            for candle in candles[end_index - length : end_index]
        ]
        if val is not None
    )


def falling(candles: List[Candle], indicator: str, length: int = 4) -> bool:
    """True if current `indicator` reading is less than any previous `indicator`
    reading for `length` bars back, False otherwise.
    Length `excludes` latest"""
    end_index = absindex(-1, len(candles))
    if end_index is None:
        return False

    if not reading_period(candles, length, indicator):
        length = reading_count(candles, indicator) - 1

    if length < 1 or len(candles) < 2:
        return False

    newest_reading = reading_by_candle(candles[-1], indicator)

    return any(
        val > newest_reading
        for val in [
            reading_by_candle(candle, indicator)
            for candle in candles[end_index - length : end_index]
        ]
        if val is not None
    )


def mean_rising(candles: List[Candle], indicator: str, length: int = 4) -> bool:
    """True if current `indicator` reading is greater than the avg of the previous
    `length` `indicator` reading bars back, False otherwise. Length `excludes` latest

    Calc:
        NewestCandle[indicator] > mean(Candles[newest] to Candles[length])"""
    end_index = absindex(-1, len(candles))
    if end_index is None:
        return False

    if not reading_period(candles, length, indicator):
        length = reading_count(candles, indicator) - 1

    if length < 1 or len(candles) < 2:
        return False

    mean = (
        sum(
            reading_by_candle(candle, indicator)
            for candle in candles[end_index - length : end_index]
        )
        / length
    )
    return round(mean, 2) < reading_by_candle(candles[-1], indicator)


def mean_falling(candles: List[Candle], indicator: str, length: int = 4) -> bool:
    """True if current `indicator` is less than the avg of the previous
    `length` `indicator` bars back, False otherwise. Length `excludes` latest

    Calc:
        NewestCandle[indicator] > mean(Candles[newest] to Candles[length])"""
    end_index = absindex(-1, len(candles))
    if end_index is None:
        return False

    if not reading_period(candles, length, indicator):
        length = reading_count(candles, indicator) - 1

    if length < 1 or len(candles) < 2:
        return False

    mean = (
        sum(
            reading_by_candle(candle, indicator)
            for candle in candles[end_index - length : end_index]
        )
        / length
    )
    return round(mean, 2) > reading_by_candle(candles[-1], indicator)


def highest(candles: List[Candle], indicator: str, length: int = 4) -> float:
    """Highest reading for a given number of bars back.
    Returns:
        Highest reading in the series.
    """
    if not reading_period(candles, length, indicator):
        length = reading_count(candles, indicator)

    return max(
        (reading_by_candle(candle, indicator) for candle in candles[-length:]),
        default=False,
    )


def lowest(candles: List[Candle], indicator: str, length: int = 4) -> float:
    """Lowest reading for a given number of bars back.
    Returns:
        Lowest reading in the series.
    """
    if not reading_period(candles, length, indicator):
        length = reading_count(candles, indicator)

    return min(
        (reading_by_candle(candle, indicator) for candle in candles[-length:]),
        default=False,
    )


def highestbar(candles: List[Candle], indicator: str, length: int = 4) -> int:
    """Highest reading offset for a given number of bars back.
    Returns:
        Offset to the lowest bar
    """
    start_index = absindex(-1, len(candles))
    if start_index is None:
        return None

    if not reading_period(candles, length, indicator):
        length = reading_count(candles, indicator)

    high = None
    distance = 0

    for dist, index in enumerate(range(start_index, start_index - length, -1)):
        current = reading_by_index(candles, indicator, index)
        if high and high < current:
            high = current
            distance = dist
        elif high is None:
            high = current

    return distance


def lowestbar(candles: List[Candle], indicator: str, length: int = 4) -> int:
    """Lowest reading offset for a given number of bars back.
    Returns:
        Offset to the lowest bar
    """
    start_index = absindex(-1, len(candles))
    if start_index is None:
        return None

    if not reading_period(candles, length, indicator):
        length = reading_count(candles, indicator)

    low = None
    distance = 0

    for dist, index in enumerate(range(start_index, start_index - length, -1)):
        current = reading_by_index(candles, indicator, index)
        if low and low > current:
            low = current
            distance = dist
        elif low is None:
            low = current

    return distance


def cross(
    candles: List[Candle], indicator_one: str, indicator_two: str, length: int = 1
) -> bool:
    """The `indicator_one` reading is defined as having crossed `indicator_two` reading.
    Either direction"""
    start_index = absindex(-1, len(candles))
    if start_index is None:
        return False

    if not reading_period(candles, length, indicator_one) or not reading_period(
        candles, length, indicator_two
    ):
        length = min(
            [reading_count(candles, indicator_one), reading_count(candles, indicator_two)]
        )
        length -= 1

    for index in range(start_index, start_index - length, -1):
        if (
            reading_by_index(candles, indicator_one, index)
            > reading_by_index(candles, indicator_two, index)
            and reading_by_index(candles, indicator_one, index - 1)
            <= reading_by_index(candles, indicator_two, index - 1)
        ) or (
            reading_by_index(candles, indicator_one, index)
            < reading_by_index(candles, indicator_two, index)
            and reading_by_index(candles, indicator_one, index - 1)
            >= reading_by_index(candles, indicator_two, index - 1)
        ):
            return True

    return False


def crossover(
    candles: List[Candle], indicator_one: str, indicator_two: str, length: int = 1
) -> bool:
    """The `indicator_one` reading is defined as having crossed over `indicator_two` reading,
    If  `indicator_two` is higher then `indicator_one` and in the last `length` it was under.
    Length is how far back to check, if length is greater then amount of candles, check all"""
    start_index = absindex(-1, len(candles))
    if start_index is None:
        return False

    if not reading_period(candles, length, indicator_one) or not reading_period(
        candles, length, indicator_two
    ):
        length = min(
            [reading_count(candles, indicator_one), reading_count(candles, indicator_two)]
        )
        length -= 1

    for index in range(start_index, start_index - length, -1):
        if reading_by_index(candles, indicator_one, index) > reading_by_index(
            candles, indicator_two, index
        ) and reading_by_index(candles, indicator_one, index - 1) <= reading_by_index(
            candles, indicator_two, index - 1
        ):
            return True

    return False


def crossunder(
    candles: List[Candle], indicator_one: str, indicator_two: str, length: int = 1
) -> bool:
    """The `indicator_one` reading is defined as having crossed under `indicator_two` reading,
    If `indicator_two` is lower then `indicator_one` and in the last `length` it was over.
    Length is how far back to check, if length is greater then amount of candles, check all"""
    start_index = absindex(-1, len(candles))
    if start_index is None:
        return False

    if not reading_period(candles, length, indicator_one) or not reading_period(
        candles, length, indicator_two
    ):
        length = min(
            [reading_count(candles, indicator_one), reading_count(candles, indicator_two)]
        )
        length -= 1

    for index in range(start_index, start_index - length, -1):
        if reading_by_index(candles, indicator_one, index) < reading_by_index(
            candles, indicator_two, index
        ) and reading_by_index(candles, indicator_one, index - 1) >= reading_by_index(
            candles, indicator_two, index - 1
        ):
            return True

    return False
