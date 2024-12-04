from typing import List, Optional

from hexital.analysis import utils
from hexital.core.candle import Candle
from hexital.core.hexital import Hexital
from hexital.core.indicator import Indicator
from hexital.utils.candles import get_readings_period, reading_by_candle, reading_by_index
from hexital.utils.indexing import absindex, valid_index
from hexital.utils.timeframe import within_timeframe


def _retrieve_candles(
    obj: Indicator | Hexital | List[Candle],
    indicator: Optional[str] = None,
    indicator_cmp: Optional[str] = None,
) -> List[List[Candle]]:
    if isinstance(obj, list):
        return [obj]
    elif isinstance(obj, Indicator):
        return [obj.candles]
    elif isinstance(obj, Hexital) and not indicator and not indicator_cmp:
        return [obj.candles("default")]
    elif isinstance(obj, Hexital) and indicator:
        return obj.find_candles(indicator, indicator_cmp)

    return []


def _timeframe_pair_candles(
    candles: List[List[Candle]],
) -> List[List[Candle]]:
    organised = [[], []]
    set_one = candles[0]
    set_two = candles[1]

    if set_one[-1].timeframe == set_two[-1].timeframe:
        return candles
    else:
        second_pointer = len(candles[1]) - 1

        for first_pointer in range(len(set_one) - 1, -1, -1):
            if second_pointer == 0:
                break

            while (
                not within_timeframe(
                    set_one[first_pointer].timestamp,
                    set_two[second_pointer].timestamp,
                    set_two[second_pointer].timeframe,
                )
                and not within_timeframe(
                    set_two[second_pointer].timestamp,
                    set_one[first_pointer].timestamp,
                    set_one[first_pointer].timeframe,
                )
            ) and second_pointer >= 0:
                second_pointer -= 1

            organised[0].insert(0, set_one[first_pointer])
            organised[1].insert(0, set_two[second_pointer])

    return organised


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
    indicator_cmp: str,
    length: int = 0,
    index: int = -1,
) -> bool:
    """Check if indicator is a higher value than indicator_cmp"""
    candles_ = _retrieve_candles(candles, indicator, indicator_cmp)

    if not candles_:
        return False

    if len(candles_) == 1 and candles_[0]:
        candle_set = candles_[0]
        idx = absindex(index, len(candle_set)) + 1
        length = idx - (length + 1)

        return _above(
            candle_set[length:idx],
            indicator,
            candle_set[length:idx],
            indicator_cmp,
        )
    elif len(candles_) == 2:
        candle_set = _timeframe_pair_candles(candles_)
        idx = absindex(index, len(candle_set[0])) + 1
        length = idx - (length + 1)

        return _above(
            candle_set[0][length:idx],
            indicator,
            candle_set[1][length:idx],
            indicator_cmp,
        )

    return False


def _above(
    candles_one: List[Candle],
    indicator_one: str,
    candles_two: List[Candle],
    indicator_cmp: str,
) -> bool:
    if len(candles_one) != len(candles_two):
        return False

    for i in range(len(candles_one)):
        reading_one = reading_by_index(candles_one, indicator_one, i)
        reading_two = reading_by_index(candles_two, indicator_cmp, i)

        if isinstance(reading_one, (float, int)) and isinstance(reading_two, (float, int)):
            if reading_one > reading_two:
                return True

    return False


def below(
    candles: Indicator | Hexital | List[Candle],
    indicator: str,
    indicator_cmp: str,
    length: int = 0,
    index: int = -1,
) -> bool:
    """Check if indicator is a lower value than indicator_cmp"""
    candles_ = _retrieve_candles(candles, indicator, indicator_cmp)

    if not candles_:
        return False

    if len(candles_) == 1 and candles_[0]:
        candle_set = candles_[0]
        idx = absindex(index, len(candle_set)) + 1
        length = idx - (length + 1)

        return _below(
            candle_set[length:idx],
            indicator,
            candle_set[length:idx],
            indicator_cmp,
        )
    elif len(candles_) == 2:
        candle_set = _timeframe_pair_candles(candles_)
        idx = absindex(index, len(candle_set[0])) + 1
        length = idx - (length + 1)

        return _below(
            candle_set[0][length:idx],
            indicator,
            candle_set[1][length:idx],
            indicator_cmp,
        )

    return False


def _below(
    candles_one: List[Candle],
    indicator_one: str,
    candles_two: List[Candle],
    indicator_cmp: str,
) -> bool:
    if len(candles_one) != len(candles_two):
        return False

    for i in range(len(candles_one)):
        reading_one = reading_by_index(candles_one, indicator_one, i)
        reading_two = reading_by_index(candles_two, indicator_cmp, i)

        if isinstance(reading_one, (float, int)) and isinstance(reading_two, (float, int)):
            if reading_one < reading_two:
                return True

    return False


def value_range(
    candles: Indicator | Hexital | List[Candle], indicator: str, length: int = 4, index: int = -1
) -> float | None:
    """Returns the difference between the min and max values in a indicator series.
    Length `includes` latest, if length is too long for amount of candles,
    will check all of them"""
    candle_set = _retrieve_candles(candles, indicator)[0]
    if not candle_set:
        return None

    readings = get_readings_period(candle_set, indicator, length, index, True)

    if len(readings) < 2:
        return None

    return abs(min(readings) - max(readings))


def rising(
    candles: Indicator | Hexital | List[Candle], indicator: str, length: int = 1, index: int = -1
) -> bool:
    """True if current `indicator` is greater than all previous `indicator`
    for `length` bars back, False otherwise.
    Length `excludes` latest"""
    candle_set = _retrieve_candles(candles, indicator)[0]

    idx = absindex(index, len(candle_set))

    if length < 1 or len(candle_set) < 2:
        return False

    latest_reading = reading_by_candle(candle_set[idx], indicator)
    if latest_reading is None or isinstance(latest_reading, dict):
        return False

    readings = get_readings_period(candle_set, indicator, length, idx)
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
    candle_set = _retrieve_candles(candles, indicator)[0]
    idx = absindex(index, len(candle_set))

    if length < 1 or len(candle_set) < 2:
        return False

    latest_reading = reading_by_candle(candle_set[idx], indicator)
    if latest_reading is None or isinstance(latest_reading, dict):
        return False

    readings = get_readings_period(candle_set, indicator, length, idx)
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
    candle_set = _retrieve_candles(candles, indicator)[0]
    idx = absindex(index, len(candle_set))

    if length < 1 or len(candle_set) < 2:
        return False

    latest_reading = reading_by_candle(candle_set[idx], indicator)
    if latest_reading is None or isinstance(latest_reading, dict):
        return False

    readings = get_readings_period(candle_set, indicator, length, idx)
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
    candle_set = _retrieve_candles(candles, indicator)[0]
    idx = absindex(index, len(candle_set))

    if length < 1 or len(candle_set) < 2:
        return False

    latest_reading = reading_by_candle(candle_set[idx], indicator)
    if latest_reading is None or isinstance(latest_reading, dict):
        return False

    readings = get_readings_period(candle_set, indicator, length, idx)
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
    return utils.highest(_retrieve_candles(candles, indicator)[0], indicator, length, index)


def lowest(
    candles: Indicator | Hexital | List[Candle], indicator: str, length: int = 4, index: int = -1
) -> float | None:
    """Lowest reading for a given number of bars back. Includes latest
    Returns:
        Lowest reading in the series.
    """
    return utils.lowest(_retrieve_candles(candles, indicator)[0], indicator, length, index)


def highestbar(
    candles: Indicator | Hexital | List[Candle], indicator: str, length: int = 4, index: int = -1
) -> int | None:
    """Highest reading offset for a given number of bars back.
    Returns:
        Offset to the lowest bar
    """
    candle_set = _retrieve_candles(candles, indicator)[0]

    if not candles:
        return None

    idx = absindex(index, len(candle_set))

    high = None
    distance = 0

    for idx, index in enumerate(range(idx, idx - length, -1)):
        current = reading_by_index(candle_set, indicator, index)
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
    candle_set = _retrieve_candles(candles, indicator)[0]
    if not candle_set:
        return None

    idx = absindex(index, len(candle_set))

    low = None
    distance = 0

    for idx, index in enumerate(range(idx, idx - length, -1)):
        current = reading_by_index(candle_set, indicator, index)
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
    indicator_cmp: str,
    length: int = 1,
    index: int = -1,
) -> bool:
    """The `indicator_one` reading is defined as having crossed `indicator_cmp` reading.
    Either direction"""
    candles_ = _retrieve_candles(candles, indicator_one, indicator_cmp)

    if not candles_:
        return False

    if len(candles_) == 1 and candles_[0]:
        candle_set = candles_[0]
        idx = absindex(index, len(candle_set)) + 1
        length = idx - (length + 1)

        return _cross(candle_set[length:idx], indicator_one, candle_set[length:idx], indicator_cmp)
    elif len(candles_) == 2:
        candle_set = _timeframe_pair_candles(candles_)
        idx = absindex(index, len(candle_set[0])) + 1
        length = idx - (length + 1)

        return _cross(
            candle_set[0][length:idx], indicator_one, candle_set[1][length:idx], indicator_cmp
        )

    return False


def _cross(
    candles_one: List[Candle],
    indicator_one: str,
    candles_two: List[Candle],
    indicator_cmp: str,
) -> bool:
    if len(candles_one) != len(candles_two):
        return False

    for i in range(len(candles_one) - 1, -1, -1):
        reading_one = reading_by_index(candles_one, indicator_one, i)
        reading_two = reading_by_index(candles_two, indicator_cmp, i)
        prev_one = reading_by_index(candles_one, indicator_one, i - 1)
        prev_two = reading_by_index(candles_two, indicator_cmp, i - 1)

        if None in [reading_one, reading_two, prev_one, prev_two]:
            continue
        elif (reading_one < reading_two and prev_one >= prev_two) or (
            reading_one > reading_two and prev_one <= prev_two
        ):
            return True

    return False


def crossover(
    candles: Indicator | Hexital | List[Candle],
    indicator_one: str,
    indicator_cmp: str,
    length: int = 1,
    index: int = -1,
) -> bool:
    """The `indicator_one` reading is defined as having crossed over `indicator_cmp` reading,
    If  `indicator_cmp` is higher then `indicator_one` and in the last `length` it was under.
    Length is how far back to check, if length is greater then amount of candles, check all"""
    candles_ = _retrieve_candles(candles, indicator_one, indicator_cmp)

    if not candles_:
        return False

    if len(candles_) == 1 and candles_[0]:
        candle_set = candles_[0]
        idx = absindex(index, len(candle_set)) + 1
        length = idx - (length + 1)

        return _crossover(
            candle_set[length:idx], indicator_one, candle_set[length:idx], indicator_cmp
        )
    elif len(candles_) == 2:
        candle_set = _timeframe_pair_candles(candles_)
        idx = absindex(index, len(candle_set[0])) + 1
        length = idx - (length + 1)

        return _crossover(
            candle_set[0][length:idx], indicator_one, candle_set[1][length:idx], indicator_cmp
        )

    return False


def _crossover(
    candles_one: List[Candle],
    indicator_one: str,
    candles_two: List[Candle],
    indicator_cmp: str,
) -> bool:
    if len(candles_one) != len(candles_two):
        return False

    for i in range(len(candles_one) - 1, -1, -1):
        reading_one = reading_by_index(candles_one, indicator_one, i)
        reading_two = reading_by_index(candles_two, indicator_cmp, i)
        prev_one = reading_by_index(candles_one, indicator_one, i - 1)
        prev_two = reading_by_index(candles_two, indicator_cmp, i - 1)

        if None in [reading_one, reading_two, prev_one, prev_two]:
            continue
        elif reading_one > reading_two and prev_one <= prev_two:
            return True

    return False


def crossunder(
    candles: Indicator | Hexital | List[Candle],
    indicator_one: str,
    indicator_cmp: str,
    length: int = 1,
    index: int = -1,
) -> bool:
    """The `indicator_one` reading is defined as having crossed under `indicator_cmp` reading,
    If `indicator_cmp` is lower then `indicator_one` and in the last `length` it was over.
    Length is how far back to check, if length is greater then amount of candles, check all"""
    candles_ = _retrieve_candles(candles, indicator_one, indicator_cmp)

    if not candles_:
        return False

    if len(candles_) == 1 and candles_[0]:
        candle_set = candles_[0]
        idx = absindex(index, len(candle_set)) + 1
        length = idx - (length + 1)

        return _crossunder(
            candle_set[length:idx], indicator_one, candle_set[length:idx], indicator_cmp
        )
    elif len(candles_) == 2:
        candle_set = _timeframe_pair_candles(candles_)
        idx = absindex(index, len(candle_set[0])) + 1
        length = idx - (length + 1)

        return _crossunder(
            candle_set[0][length:idx], indicator_one, candle_set[1][length:idx], indicator_cmp
        )

    return False


def _crossunder(
    candles_one: List[Candle],
    indicator_one: str,
    candles_two: List[Candle],
    indicator_cmp: str,
) -> bool:
    if len(candles_one) != len(candles_two):
        return False

    for i in range(len(candles_one) - 1, -1, -1):
        reading_one = reading_by_index(candles_one, indicator_one, i)
        reading_two = reading_by_index(candles_two, indicator_cmp, i)
        prev_one = reading_by_index(candles_one, indicator_one, i - 1)
        prev_two = reading_by_index(candles_two, indicator_cmp, i - 1)

        if None in [reading_one, reading_two, prev_one, prev_two]:
            continue
        elif reading_one < reading_two and prev_one >= prev_two:
            return True

    return False


def flipped(
    candles: Indicator | Hexital | List[Candle], indicator: str, length: int = 1, index: int = -1
) -> bool:
    """The `indicator` reading is defined as having flipped if reading if it's different to it's
    previous reading and in the last `length` it was over.
    Length is how far back to check, if length is greater then amount of candles, check all"""
    candle_set = _retrieve_candles(candles, indicator)[0]
    if not candle_set:
        return False

    idx = absindex(index, len(candle_set))

    for idx in range(idx, idx - length, -1):
        if reading_by_index(candle_set, indicator, idx) != reading_by_index(
            candle_set, indicator, idx - 1
        ):
            return True

    return False
