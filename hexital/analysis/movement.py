from typing import List, Optional

from hexital.analysis import utils
from hexital.core.candle import Candle
from hexital.core.hexital import Hexital
from hexital.core.indicator import Indicator
from hexital.utils.candles import get_readings_period, reading_by_candle, reading_by_index
from hexital.utils.indexing import absindex, valid_index


def _retrieve_candles(
    obj: Indicator | Hexital | List[Candle],
    indicator: Optional[str] = None,
    indicator_2: Optional[str] = None,
) -> List[Candle]:
    if isinstance(obj, list):
        return obj
    elif isinstance(obj, Indicator):
        return obj.candles
    elif isinstance(obj, Hexital) and not indicator and not indicator_2:
        return obj.candles("default")
    elif isinstance(obj, Hexital) and indicator:
        return obj.find_candles(indicator, indicator_2)
    return []


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


def above(
    candles: Indicator | Hexital | List[Candle],
    indicator: str,
    indicator_two: str,
    index: int = -1,
) -> bool:
    """Check if indicator is a higher value than indicator_two"""
    candles = _retrieve_candles(candles)
    if not candles:
        return False

    index_ = absindex(index, len(candles))

    reading_one = reading_by_index(candles, indicator, index_)
    reading_two = reading_by_index(candles, indicator_two, index_)

    if isinstance(reading_one, (float, int)) and isinstance(reading_two, (float, int)):
        return reading_one > reading_two
    return False


def below(
    candles: Indicator | Hexital | List[Candle],
    indicator: str,
    indicator_two: str,
    index: int = -1,
) -> bool:
    """Check if indicator is a lower value than indicator_two"""
    candles = _retrieve_candles(candles)
    if not candles:
        return False

    index_ = absindex(index, len(candles))

    reading_one = reading_by_index(candles, indicator, index_)
    reading_two = reading_by_index(candles, indicator_two, index_)

    if isinstance(reading_one, (float, int)) and isinstance(reading_two, (float, int)):
        return reading_one < reading_two
    return False


def value_range(
    candles: Indicator | Hexital | List[Candle], indicator: str, length: int = 4, index: int = -1
) -> float | None:
    """Returns the difference between the min and max values in a indicator series.
    Length `includes` latest, if lenth is too long for amount of candles,
    will check all of them"""
    candles = _retrieve_candles(candles)
    if length < 2 or len(candles) < 2:
        return None

    readings = get_readings_period(candles, indicator, length, index, True)

    if len(readings) < 2:
        return None

    return abs(min(readings) - max(readings))


def rising(
    candles: Indicator | Hexital | List[Candle], indicator: str, length: int = 1, index: int = -1
) -> bool:
    """True if current `indicator` is greater than all previous `indicator`
    for `length` bars back, False otherwise.
    Length `excludes` latest"""
    candles = _retrieve_candles(candles)
    index_ = absindex(index, len(candles))

    if length < 1 or len(candles) < 2:
        return False

    latest_reading = reading_by_candle(candles[index_], indicator)
    if latest_reading is None or isinstance(latest_reading, dict):
        return False

    readings = get_readings_period(candles, indicator, length, index_)
    if not readings:
        return False

    for reading in readings:
        if reading >= latest_reading:
            return False
    return True


def falling(
    candles: Indicator | Hexital | List[Candle], indicator: str, length: int = 1, index: int = -1
) -> bool:
    """True if current `indicator` reading is less than all previous `indicator`
    reading for `length` bars back, False otherwise.
    Length `excludes` latest"""
    candles = _retrieve_candles(candles)
    index_ = absindex(index, len(candles))

    if length < 1 or len(candles) < 2:
        return False

    latest_reading = reading_by_candle(candles[index_], indicator)
    if latest_reading is None or isinstance(latest_reading, dict):
        return False

    readings = get_readings_period(candles, indicator, length, index_)
    if not readings:
        return False

    for reading in readings:
        if reading <= latest_reading:
            return False
    return True


def mean_rising(
    candles: Indicator | Hexital | List[Candle], indicator: str, length: int = 4, index: int = -1
) -> bool:
    """True if current `indicator` reading is greater than the avg of the previous
    `length` `indicator` reading bars back, False otherwise. Length `excludes` latest

    Calc:
        NewestCandle[indicator] > mean(Candles[newest] to Candles[length])"""
    candles = _retrieve_candles(candles)
    index_ = absindex(index, len(candles))

    if length < 1 or len(candles) < 2:
        return False

    latest_reading = reading_by_candle(candles[index_], indicator)
    if latest_reading is None or isinstance(latest_reading, dict):
        return False

    readings = get_readings_period(candles, indicator, length, index_)
    if not readings:
        return False

    return sum(readings) / len(readings) < latest_reading


def mean_falling(
    candles: Indicator | Hexital | List[Candle], indicator: str, length: int = 4, index: int = -1
) -> bool:
    """True if current `indicator` is less than the avg of the previous
    `length` `indicator` bars back, False otherwise. Length `excludes` latest

    Calc:
        NewestCandle[indicator] > mean(Candles[newest] to Candles[length])"""
    candles = _retrieve_candles(candles)
    index_ = absindex(index, len(candles))

    if length < 1 or len(candles) < 2:
        return False

    latest_reading = reading_by_candle(candles[index_], indicator)
    if latest_reading is None or isinstance(latest_reading, dict):
        return False

    readings = get_readings_period(candles, indicator, length, index_)
    if not readings:
        return False

    return sum(readings) / len(readings) > latest_reading


def highest(
    candles: Indicator | Hexital | List[Candle], indicator: str, length: int = 4, index: int = -1
) -> float | None:
    """Highest reading for a given number of bars back. Includes latest
    Returns:
        Highest reading in the series.
    """
    return utils.highest(_retrieve_candles(candles), indicator, length, index)


def lowest(
    candles: Indicator | Hexital | List[Candle], indicator: str, length: int = 4, index: int = -1
) -> float | None:
    """Lowest reading for a given number of bars back. Includes latest
    Returns:
        Lowest reading in the series.
    """
    return utils.lowest(_retrieve_candles(candles), indicator, length, index)


def highestbar(
    candles: Indicator | Hexital | List[Candle], indicator: str, length: int = 4, index: int = -1
) -> int | None:
    """Highest reading offset for a given number of bars back.
    Returns:
        Offset to the lowest bar
    """
    candles = _retrieve_candles(candles)
    if not candles:
        return None

    index_ = absindex(index, len(candles))

    high = None
    distance = 0

    for idx, index in enumerate(range(index_, index_ - length, -1)):
        current = reading_by_index(candles, indicator, index)
        if not isinstance(current, (float, int)):
            continue

        if high is None:
            high = current

        if high < current:
            high = current
            distance = idx

    return distance


def lowestbar(
    candles: Indicator | Hexital | List[Candle], indicator: str, length: int = 4, index: int = -1
) -> int | None:
    """Lowest reading offset for a given number of bars back.
    Returns:
        Offset to the lowest bar
    """
    candles = _retrieve_candles(candles)
    if not candles:
        return None

    index_ = absindex(index, len(candles))

    low = None
    distance = 0

    for idx, index in enumerate(range(index_, index_ - length, -1)):
        current = reading_by_index(candles, indicator, index)
        if not isinstance(current, (float, int)):
            continue

        if low is None:
            low = current

        if low > current:
            low = current
            distance = idx

    return distance


def cross(
    candles: Indicator | Hexital | List[Candle],
    indicator_one: str,
    indicator_two: str,
    length: int = 1,
    index: int = -1,
) -> bool:
    """The `indicator_one` reading is defined as having crossed `indicator_two` reading.
    Either direction"""
    candles = _retrieve_candles(candles)
    if not candles:
        return False

    index_ = absindex(index, len(candles))

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
    candles: Indicator | Hexital | List[Candle],
    indicator_one: str,
    indicator_two: str,
    length: int = 1,
    index: int = -1,
) -> bool:
    """The `indicator_one` reading is defined as having crossed over `indicator_two` reading,
    If  `indicator_two` is higher then `indicator_one` and in the last `length` it was under.
    Length is how far back to check, if length is greater then amount of candles, check all"""
    candles = _retrieve_candles(candles)
    if not candles:
        return False

    index_ = absindex(index, len(candles))

    for idx in range(index_, index_ - length, -1):
        if above(candles, indicator_one, indicator_two, idx) and below(
            candles, indicator_one, indicator_two, idx - 1
        ):
            return True

    return False


def crossunder(
    candles: Indicator | Hexital | List[Candle],
    indicator_one: str,
    indicator_two: str,
    length: int = 1,
    index: int = -1,
) -> bool:
    """The `indicator_one` reading is defined as having crossed under `indicator_two` reading,
    If `indicator_two` is lower then `indicator_one` and in the last `length` it was over.
    Length is how far back to check, if length is greater then amount of candles, check all"""
    candles = _retrieve_candles(candles)
    if not candles:
        return False

    index_ = absindex(index, len(candles))

    for idx in range(index_, index_ - length, -1):
        if below(candles, indicator_one, indicator_two, idx) and above(
            candles, indicator_one, indicator_two, idx - 1
        ):
            return True

    return False


def flipped(
    candles: Indicator | Hexital | List[Candle], indicator: str, length: int = 1, index: int = -1
) -> bool:
    """The `indicator` reading is defined as having flipped if reading if it's different to it's
    previous reading and in the last `length` it was over.
    Length is how far back to check, if length is greater then amount of candles, check all"""
    candles = _retrieve_candles(candles)
    if not candles:
        return False

    index_ = absindex(index, len(candles))

    for idx in range(index_, index_ - length, -1):
        if reading_by_index(candles, indicator, idx) != reading_by_index(
            candles, indicator, idx - 1
        ):
            return True

    return False
