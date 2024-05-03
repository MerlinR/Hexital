from typing import List

from hexital.core.candle import Candle
from hexital.utils.candles import (
    reading_by_candle,
    reading_by_index,
)
from hexital.utils.indexing import absindex, valid_index


def _get_clean_readings(
    candles: List[Candle], indicator: str, length: int, index: int, include_latest: bool = False
) -> List[float | int]:
    """Goes through from index-length to index and returns a list of values, removes dict's and None values
    Returns from newest at the front (reversed)"""
    to_index = index
    if include_latest:
        to_index += 1

    start = index - length
    if start < 0:
        start = 0

    readings = [reading_by_candle(candle, indicator) for candle in candles[start:to_index]]
    return [reading for reading in reversed(readings) if isinstance(reading, (float, int))]


def positive(candles: Candle | List[Candle], index: int = -1) -> bool:
    if isinstance(candles, Candle):
        return candles.positive

    if not valid_index(index, len(candles)):
        return False
    return candles[index].positive


def negative(candles: Candle | List[Candle], index: int = -1) -> bool:
    if isinstance(candles, Candle):
        return candles.negative

    if not valid_index(index, len(candles)):
        return False
    return candles[index].negative


def above(candles: List[Candle], indicator: str, indicator_two: str, index: int = -1) -> bool:
    """Check if indicator is a higher value than indicator_two"""
    if not candles:
        return False

    reading_one = reading_by_index(candles, indicator, index)
    reading_two = reading_by_index(candles, indicator_two, index)

    if reading_one is not None and reading_two is not None:
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
    if index_ is None or length < 2:
        return None

    readings = _get_clean_readings(candles, indicator, length, index_, True)

    if len(readings) < 2:
        return None

    return abs(min(readings) - max(readings))


def rising(candles: List[Candle], indicator: str, length: int = 1, index: int = -1) -> bool:
    """True if current `indicator` is greater than all previous `indicator`
    for `length` bars back, False otherwise.
    Length `excludes` latest"""
    index_ = absindex(index, len(candles))

    if index_ is None or length < 1 or len(candles) < 2:
        return False

    latest_reading = reading_by_candle(candles[index], indicator)
    if latest_reading is None or isinstance(latest_reading, dict):
        return False

    readings = _get_clean_readings(candles, indicator, length, index_)
    if not readings:
        return False

    for reading in readings:
        if reading >= latest_reading:
            return False
    return True


def falling(candles: List[Candle], indicator: str, length: int = 1, index: int = -1) -> bool:
    """True if current `indicator` reading is less than all previous `indicator`
    reading for `length` bars back, False otherwise.
    Length `excludes` latest"""
    index_ = absindex(index, len(candles))
    if index_ is None or length < 1 or len(candles) < 2:
        return False

    latest_reading = reading_by_candle(candles[index], indicator)
    if latest_reading is None or isinstance(latest_reading, dict):
        return False

    readings = _get_clean_readings(candles, indicator, length, index_)
    if not readings:
        return False

    for reading in readings:
        if reading <= latest_reading:
            return False
    return True


def mean_rising(candles: List[Candle], indicator: str, length: int = 4, index: int = -1) -> bool:
    """True if current `indicator` reading is greater than the avg of the previous
    `length` `indicator` reading bars back, False otherwise. Length `excludes` latest

    Calc:
        NewestCandle[indicator] > mean(Candles[newest] to Candles[length])"""
    index_ = absindex(index, len(candles))
    if index_ is None or length < 1 or len(candles) < 2:
        return False

    latest_reading = reading_by_candle(candles[index_], indicator)
    if latest_reading is None or isinstance(latest_reading, dict):
        return False

    readings = _get_clean_readings(candles, indicator, length, index_)
    if not readings:
        return False

    return sum(readings) / len(readings) < latest_reading


def mean_falling(candles: List[Candle], indicator: str, length: int = 4, index: int = -1) -> bool:
    """True if current `indicator` is less than the avg of the previous
    `length` `indicator` bars back, False otherwise. Length `excludes` latest

    Calc:
        NewestCandle[indicator] > mean(Candles[newest] to Candles[length])"""
    index_ = absindex(index, len(candles))
    if index_ is None or length < 1 or len(candles) < 2:
        return False

    latest_reading = reading_by_candle(candles[index_], indicator)
    if latest_reading is None or isinstance(latest_reading, dict):
        return False

    readings = _get_clean_readings(candles, indicator, length, index_)
    if not readings:
        return False

    return sum(readings) / len(readings) > latest_reading


def highest(
    candles: List[Candle], indicator: str, length: int = 4, index: int = -1
) -> float | None:
    """Highest reading for a given number of bars back.
    Returns:
        Highest reading in the series.
    """
    index_ = absindex(index, len(candles))
    if index_ is None or length < 1 or not len(candles):
        return False

    readings = _get_clean_readings(candles, indicator, length, index_, True)

    max_reading = max(readings, default=False)
    return max_reading if max_reading is not False else None


def lowest(
    candles: List[Candle], indicator: str, length: int = 4, index: int = -1
) -> float | None:
    """Lowest reading for a given number of bars back.
    Returns:
        Lowest reading in the series.
    """
    index_ = absindex(index, len(candles))
    if index_ is None or length < 1 or not len(candles):
        return False

    readings = _get_clean_readings(candles, indicator, length, index_, True)

    min_reading = min(readings, default=False)

    return min_reading if min_reading is not False else None


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

    high = None
    distance = 0

    for idx, index in enumerate(range(index_, index_ - length, -1)):
        current = reading_by_index(candles, indicator, index)
        if current is None:
            continue

        if high is None:
            high = current

        if high < current:
            high = current
            distance = idx

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

    low = None
    distance = 0

    for idx, index in enumerate(range(index_, index_ - length, -1)):
        current = reading_by_index(candles, indicator, index)
        if current is None:
            continue

        if low is None:
            low = current

        if low > current:
            low = current
            distance = idx

    return distance


def cross(
    candles: List[Candle], indicator_one: str, indicator_two: str, length: int = 1, index: int = -1
) -> bool:
    """The `indicator_one` reading is defined as having crossed `indicator_two` reading.
    Either direction"""
    index_ = absindex(index, len(candles))
    if index_ is None:
        return False

    for idx in range(index_, index_ - length, -1):
        reading_one = reading_by_index(candles, indicator_two, idx)
        reading_two = reading_by_index(candles, indicator_one, idx)
        prev_one = reading_by_index(candles, indicator_one, idx - 1)
        prev_two = reading_by_index(candles, indicator_two, idx - 1)

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

    for idx in range(index_, index_ - length, -1):
        if above(candles, indicator_one, indicator_two, idx) and below(
            candles, indicator_one, indicator_two, idx - 1
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

    for idx in range(index_, index_ - length, -1):
        if below(candles, indicator_one, indicator_two, idx) and above(
            candles, indicator_one, indicator_two, idx - 1
        ):
            return True

    return False
