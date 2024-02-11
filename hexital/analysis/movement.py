from typing import List

from hexital.core.candle import Candle
from hexital.utils.candles import (
    reading_by_candle,
    reading_by_index,
    reading_count,
    reading_period,
)
from hexital.utils.indexing import absindex, valid_index


def _get_clean_readings(
    candles: List[Candle], indicator: str, length: int, index: int, include_latest: bool = False
) -> List[float | int]:
    """Goes through from index-length to index and returns a list of values, removes dict's and None values"""
    to_index = index
    if include_latest:
        to_index += 1

    readings = [
        reading_by_candle(candle, indicator) for candle in candles[index - length : to_index]
    ]
    return [reading for reading in readings if isinstance(reading, (float, int))]


def positive(candles: Candle | List[Candle], index: int = -1) -> bool:
    if isinstance(candles, Candle):
        return candles.positive()

    if not valid_index(index, len(candles)):
        return False
    return candles[index].positive()


def negative(candles: Candle | List[Candle], index: int = -1) -> bool:
    if isinstance(candles, Candle):
        return candles.negative()

    if not valid_index(index, len(candles)):
        return False
    return candles[index].negative()


def above(candles: List[Candle], indicator: str, indicator_two: str, index: int = -1) -> bool:
    """Check if indicator is a higher value than indicator_two"""
    if not candles:
        return False

    reading_one = reading_by_index(candles, indicator, index)
    reading_two = reading_by_index(candles, indicator_two, index)

    if isinstance(reading_one, (float, int)) and isinstance(reading_two, (float, int)):
        return reading_one > reading_two
    return False


def below(candles: List[Candle], indicator: str, indicator_two: str, index: int = -1) -> bool:
    """Check if indicator is a lower value than indicator_two"""
    if not candles:
        return False

    reading_one = reading_by_index(candles, indicator, index)
    reading_two = reading_by_index(candles, indicator_two, index)

    if isinstance(reading_one, (float, int)) and isinstance(reading_two, (float, int)):
        return reading_one < reading_two
    return False


def value_range(
    candles: List[Candle], indicator: str, length: int = 4, index: int = -1
) -> float | None:
    """Returns the difference between the min and max values in a indicator series.
    Length `includes` latest, if lenth is too long for amount of candles,
    will check all of them"""
    index_ = absindex(index, len(candles))
    if index_ is None:
        return None

    if not reading_period(candles, length, indicator):
        length = reading_count(candles, indicator) - 1

    if length < 2:
        return None

    readings = _get_clean_readings(candles, indicator, length, index_, True)

    return abs(min(readings) - max(readings))


def rising(candles: List[Candle], indicator: str, length: int = 4, index: int = -1) -> bool:
    """True if current `indicator` is greater than all previous `indicator`
    for `length` bars back, False otherwise.
    Length `excludes` latest"""
    index_ = absindex(index, len(candles))
    if index_ is None:
        return False

    if not reading_period(candles, length, indicator):
        length = reading_count(candles, indicator) - 1

    if length < 1 or len(candles) < 2:
        return False

    latest_reading = reading_by_candle(candles[-1], indicator)
    if latest_reading is None or isinstance(latest_reading, dict):
        return False

    readings = _get_clean_readings(candles, indicator, length, index_)

    return all(reading < latest_reading for reading in readings)


def falling(candles: List[Candle], indicator: str, length: int = 4, index: int = -1) -> bool:
    """True if current `indicator` reading is less than all previous `indicator`
    reading for `length` bars back, False otherwise.
    Length `excludes` latest"""
    index_ = absindex(index, len(candles))
    if index_ is None:
        return False

    if not reading_period(candles, length, indicator):
        length = reading_count(candles, indicator) - 1

    if length < 1 or len(candles) < 2:
        return False

    latest_reading = reading_by_candle(candles[-1], indicator)
    if latest_reading is None or isinstance(latest_reading, dict):
        return False

    readings = _get_clean_readings(candles, indicator, length, index_)

    return all(reading > latest_reading for reading in readings)


def mean_rising(candles: List[Candle], indicator: str, length: int = 4, index: int = -1) -> bool:
    """True if current `indicator` reading is greater than the avg of the previous
    `length` `indicator` reading bars back, False otherwise. Length `excludes` latest

    Calc:
        NewestCandle[indicator] > mean(Candles[newest] to Candles[length])"""
    index_ = absindex(index, len(candles))
    if index_ is None:
        return False

    if not reading_period(candles, length, indicator):
        length = reading_count(candles, indicator) - 1

    if length < 1 or len(candles) < 2:
        return False

    latest_reading = reading_by_candle(candles[-1], indicator)
    if latest_reading is None or isinstance(latest_reading, dict):
        return False

    readings = _get_clean_readings(candles, indicator, length, index_)

    mean = sum(reading for reading in readings) / length
    return round(mean, 2) < latest_reading


def mean_falling(candles: List[Candle], indicator: str, length: int = 4, index: int = -1) -> bool:
    """True if current `indicator` is less than the avg of the previous
    `length` `indicator` bars back, False otherwise. Length `excludes` latest

    Calc:
        NewestCandle[indicator] > mean(Candles[newest] to Candles[length])"""
    index_ = absindex(index, len(candles))
    if index_ is None:
        return False

    if not reading_period(candles, length, indicator):
        length = reading_count(candles, indicator) - 1

    if length < 1 or len(candles) < 2:
        return False

    latest_reading = reading_by_candle(candles[-1], indicator)
    if latest_reading is None or isinstance(latest_reading, dict):
        return False

    readings = _get_clean_readings(candles, indicator, length, index_)

    mean = sum(reading for reading in readings) / length
    return round(mean, 2) > latest_reading


def highest(
    candles: List[Candle], indicator: str, length: int = 4, index: int = -1
) -> float | bool:
    """Highest reading for a given number of bars back.
    Returns:
        Highest reading in the series.
    """
    index_ = absindex(index, len(candles))
    if index_ is None:
        return False

    if not reading_period(candles, length, indicator, index_):
        length = reading_count(candles, indicator) - 1

    readings = _get_clean_readings(candles, indicator, length, index_, True)

    return max([reading for reading in readings], default=False)


def lowest(
    candles: List[Candle], indicator: str, length: int = 4, index: int = -1
) -> float | bool:
    """Lowest reading for a given number of bars back.
    Returns:
        Lowest reading in the series.
    """
    index_ = absindex(index, len(candles))
    if index_ is None:
        return False

    if not reading_period(candles, length, indicator):
        length = reading_count(candles, indicator) - 1

    readings = _get_clean_readings(candles, indicator, length, index_, True)

    return min([reading for reading in readings], default=False)


def highestbar(
    candles: List[Candle], indicator: str, length: int = 4, index: int = -1
) -> int | None:
    """Highest reading offset for a given number of bars back.
    Returns:
        Offset to the lowest bar
    """
    index_ = absindex(index, len(candles))
    if index_ is None:
        return None

    if not reading_period(candles, length, indicator):
        length = reading_count(candles, indicator)

    high = None
    distance = 0

    for dist, index in enumerate(range(index_, index_ - length, -1)):
        current = reading_by_index(candles, indicator, index)
        if current is None or isinstance(current, dict):
            break

        if high and high < current:
            high = current
            distance = dist
        elif high is None:
            high = current

    return distance


def lowestbar(
    candles: List[Candle], indicator: str, length: int = 4, index: int = -1
) -> int | None:
    """Lowest reading offset for a given number of bars back.
    Returns:
        Offset to the lowest bar
    """
    index_ = absindex(index, len(candles))
    if index_ is None:
        return None

    if not reading_period(candles, length, indicator):
        length = reading_count(candles, indicator)

    low = None
    distance = 0

    for dist, index in enumerate(range(index_, index_ - length, -1)):
        current = reading_by_index(candles, indicator, index)
        if current is None or isinstance(current, dict):
            break

        if low and low > current:
            low = current
            distance = dist
        elif low is None:
            low = current

    return distance


def cross(
    candles: List[Candle], indicator_one: str, indicator_two: str, length: int = 1, index: int = -1
) -> bool:
    """The `indicator_one` reading is defined as having crossed `indicator_two` reading.
    Either direction"""
    index_ = absindex(index, len(candles))
    if index_ is None:
        return False

    if not reading_period(candles, length, indicator_one) or not reading_period(
        candles, length, indicator_two
    ):
        length = (
            min([reading_count(candles, indicator_one), reading_count(candles, indicator_two)]) - 1
        )

    for index in range(index_, index_ - length, -1):
        reading_one = reading_by_index(candles, indicator_two, index)
        reading_two = reading_by_index(candles, indicator_one, index)
        prev_one = reading_by_index(candles, indicator_one, index - 1)
        prev_two = reading_by_index(candles, indicator_two, index - 1)

        if (reading_one < reading_two and prev_one <= prev_two) or (
            reading_one > reading_two and prev_one >= prev_two
        ):
            return True

    return False


def crossover(
    candles: List[Candle], indicator_one: str, indicator_two: str, length: int = 1, index: int = -1
) -> bool:
    """The `indicator_one` reading is defined as having crossed over `indicator_two` reading,
    If  `indicator_two` is higher then `indicator_one` and in the last `length` it was under.
    Length is how far back to check, if length is greater then amount of candles, check all"""
    index_ = absindex(index, len(candles))
    if index_ is None:
        return False

    if not reading_period(candles, length, indicator_one) or not reading_period(
        candles, length, indicator_two
    ):
        length = (
            min([reading_count(candles, indicator_one), reading_count(candles, indicator_two)]) - 1
        )

    for index in range(index_, index_ - length, -1):
        if above(candles, indicator_one, indicator_two, index) and below(
            candles, indicator_one, indicator_two, index - 1
        ):
            return True

    return False


def crossunder(
    candles: List[Candle], indicator_one: str, indicator_two: str, length: int = 1, index: int = -1
) -> bool:
    """The `indicator_one` reading is defined as having crossed under `indicator_two` reading,
    If `indicator_two` is lower then `indicator_one` and in the last `length` it was over.
    Length is how far back to check, if length is greater then amount of candles, check all"""
    index_ = absindex(index, len(candles))
    if index_ is None:
        return False

    if not reading_period(candles, length, indicator_one) or not reading_period(
        candles, length, indicator_two
    ):
        length = (
            min([reading_count(candles, indicator_one), reading_count(candles, indicator_two)]) - 1
        )

    for index in range(index_, index_ - length, -1):
        if below(candles, indicator_one, indicator_two, index) and above(
            candles, indicator_one, indicator_two, index - 1
        ):
            return True

    return False
