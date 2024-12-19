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
    """Above Analysis

    Checks whether the `indicator` reading is higher than the `indicator_cmp` reading.
    By default, it evaluates the latest candle but can also check `n` candles back.
    If any candle within the specified range is above, it returns `True`.

    Args:
        candles (Indicator | Hexital | List[Candle]): The data source containing the indicators.
        indicator (str): The primary indicator to evaluate.
        indicator_cmp (str): The secondary indicator to compare against.
        length (int, optional):  The number of candles to include in the range. Defaults to 0 (only the current index).
        index (int, optional): The index to start the evaluation. Defaults to -1 (latest candle).

    Returns:
        bool: `True` if `indicator` is above `indicator_cmp` within the specified range; otherwise `False`.
    """
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
    candles: List[Candle],
    indicator: str,
    candles_two: List[Candle],
    indicator_cmp: str,
) -> bool:
    if len(candles) != len(candles_two):
        return False

    for i in range(len(candles)):
        reading_one = reading_by_index(candles, indicator, i)
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
    """Below Analysis

    Checks whether the `indicator` reading is lower than the `indicator_cmp` reading.
    By default, it evaluates the latest candle but can also check `n` candles back.
    If any candle within the specified range is below, it returns `True`.

    Args:
        candles (Indicator | Hexital | List[Candle]): The data source containing the indicators.
        indicator (str): The primary indicator to evaluate.
        indicator_cmp (str): The secondary indicator to compare against.
        length (int, optional): The number of candles to include in the range. Defaults to 0 (only the current index).
        index (int, optional): The index to start the evaluation. Defaults to -1 (latest candle).

    Returns:
        bool: `True` if `indicator` is below `indicator_cmp` within the specified range; otherwise `False`.
    """
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
    candles: List[Candle],
    indicator: str,
    candles_two: List[Candle],
    indicator_cmp: str,
) -> bool:
    if len(candles) != len(candles_two):
        return False

    for i in range(len(candles)):
        reading_one = reading_by_index(candles, indicator, i)
        reading_two = reading_by_index(candles_two, indicator_cmp, i)

        if isinstance(reading_one, (float, int)) and isinstance(reading_two, (float, int)):
            if reading_one < reading_two:
                return True

    return False


def value_range(
    candles: Indicator | Hexital | List[Candle], indicator: str, length: int = 4, index: int = -1
) -> float | None:
    """Value Range Analysis

    Calculates the difference between the minimum and maximum values for the given `indicator`
    within a specified range of candles. Includes the latest candle by default. If the specified
    length exceeds the available candles, it will evaluate all candles.

    Args:
        candles (Indicator | Hexital | List[Candle]): The data source containing the indicators.
        indicator (str): The name of the indicator to evaluate.
        length (int, optional): The number of candles to include in the range. Defaults to 4.
        index (int, optional): The index to start the evaluation. Defaults to -1 (latest candle).

    Returns:
        float | None: The difference between the minimum and maximum indicator values in the range,
        or `None` if there are insufficient readings.
    """
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
    """Rising Analysis

    Determines whether the `indicator` consistently rises across a specified range of candles.
    By default, it checks if the current indicator value is greater than the previous one.

    Args:
        candles (Indicator | Hexital | List[Candle]): The data source containing the indicators.
        indicator (str): The name of the indicator to evaluate.
        length (int, optional): The number of candles to include in the range. Defaults to 1.
            (compares the latest with the previous).
        index (int, optional): The index to start the evaluation. Defaults to -1 (latest candle).

    Returns:
        bool: `True` if the `indicator` is greater than each previous readings in the range; otherwise `False`.
    """
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
    """Falling Analysis

    Determines whether the `indicator` consistently falling across a specified range of candles.
    By default, it checks if the current indicator value is lower than the previous one.

    Args:
        candles (Indicator | Hexital | List[Candle]): The data source containing the indicators.
        indicator (str): The name of the indicator to evaluate.
        length (int, optional): The number of candles to include in the range. Defaults to 1.
            (compares the latest with the previous).
        index (int, optional): The index to start the evaluation. Defaults to -1 (latest candle).

    Returns:
        bool: `True` if the `indicator` is lower than each previous readings in the range; otherwise `False`.
    """
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
    """Mean Rising Analysis

    Evaluates whether the `indicator` is, on average, rising across a specified range of candles.
    By default, it checks if the current indicator value is higher than the average of the previous four readings.

    Args:
        candles (Indicator | Hexital | List[Candle]): The data source containing the indicators.
        indicator (str): The name of the indicator to evaluate.
        length (int, optional): The number of candles to include in the range. Defaults to 4.
        index (int, optional): The index to start the evaluation. Defaults to -1 (latest candle).

    Returns:
        bool: `True` if the `indicator` is higher than the average of the specified `n` readings; otherwise `False`.
    """

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
    """Mean Falling Analysis

    Evaluates whether the `indicator` is, on average, falling across a specified range of candles.
    By default, it checks if the current indicator value is lower than the average of the previous four readings.

    Args:
        candles (Indicator | Hexital | List[Candle]): The data source containing the indicators.
        indicator (str): The name of the indicator to evaluate.
        length (int, optional): The number of candles to include in the range. Defaults to 4.
        index (int, optional): The index to start the evaluation. Defaults to -1 (latest candle).

    Returns:
        bool: `True` if the `indicator` is lower than the average of the specified `n` readings; otherwise `False`.
    """
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
    """Highest Reading Analysis

    Determines the highest value of the specified `indicator` over a given number of candles.
    By default, includes the latest candle and evaluates up to the previous four candles.

    Args:
        candles (Indicator | Hexital | List[Candle]): The data source containing the indicators.
        indicator (str): The name of the indicator to evaluate.
        length (int, optional): The number of candles to include in the range. Defaults to 4.
        index (int, optional): The index to start the evaluation. Defaults to -1 (latest candle).

    Returns:
        float | None: The highest reading for the specified `indicator` within the range,
        or `None` if no valid readings are found.
    """
    return utils.highest(_retrieve_candles(candles, indicator)[0], indicator, length, index)


def lowest(
    candles: Indicator | Hexital | List[Candle], indicator: str, length: int = 4, index: int = -1
) -> float | None:
    """Lowest Reading Analysis

    Determines the lowest value of the specified `indicator` over a given number of candles.
    By default, includes the latest candle and evaluates up to the previous four candles.

    Args:
        candles (Indicator | Hexital | List[Candle]): The data source containing the indicators.
        indicator (str): The name of the indicator to evaluate.
        length (int, optional): The number of candles to include in the range. Defaults to 4.
        index (int, optional): The index to start the evaluation. Defaults to -1 (latest candle).

    Returns:
        float | None: The lowest reading for the specified `indicator` within the range,
        or `None` if no valid readings are found.
    """
    return utils.lowest(_retrieve_candles(candles, indicator)[0], indicator, length, index)


def highestbar(
    candles: Indicator | Hexital | List[Candle], indicator: str, length: int = 4, index: int = -1
) -> int | None:
    """Highest Bar Offset Analysis

    Determines the offset (distance) to the candle with the highest reading of the specified `indicator`
    within a given range. By default, includes the latest candle and evaluates up to the previous four candles.

    Args:
        candles (Indicator | Hexital | List[Candle]): The data source containing the indicators.
        indicator (str): The name of the indicator to evaluate.
        length (int, optional): The number of candles to include in the range. Defaults to 4.
        index (int, optional): The index to start the evaluation. Defaults to -1 (latest candle).

    Returns:
        int | None: The offset to the candle with the highest reading, relative to the starting index,
        or `None` if no valid readings are found.
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
    """Lowest Bar Offset Analysis

    Determines the offset (distance) to the candle with the lowest reading of the specified `indicator`
    within a given range. By default, includes the latest candle and evaluates up to the previous four candles.

    Args:
        candles (Indicator | Hexital | List[Candle]): The data source containing the indicators.
        indicator (str): The name of the indicator to evaluate.
        length (int, optional): The number of candles to include in the range. Defaults to 4.
        index (int, optional): The index to start the evaluation. Defaults to -1 (latest candle).

    Returns:
        int | None: The offset to the candle with the lowest reading, relative to the starting index,
        or `None` if no valid readings are found.
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
    indicator: str,
    indicator_cmp: str,
    length: int = 1,
    index: int = -1,
) -> bool:
    """Cross Analysis

    Determines whether the `indicator` reading has crossed the `indicator_cmp` reading
    within a specified range of candles. The cross can occur in either direction.

    Args:
        candles (Indicator | Hexital | List[Candle]): The data source containing the indicators.
        indicator (str): The primary indicator to evaluate.
        indicator_cmp (str): The secondary indicator to compare against.
        length (int, optional): The number of candles to include in the range. Defaults to 1.
            (compares the latest with the previous).
        index (int, optional): The index to start the evaluation. Defaults to -1 (latest candle).

    Returns:
        bool: `True` if `indicator` has crossed `indicator_cmp` within the specified range; otherwise `False`.
    """
    candles_ = _retrieve_candles(candles, indicator, indicator_cmp)

    if not candles_:
        return False

    if len(candles_) == 1 and candles_[0]:
        candle_set = candles_[0]
        idx = absindex(index, len(candle_set)) + 1
        length = idx - (length + 1)

        return _cross(candle_set[length:idx], indicator, candle_set[length:idx], indicator_cmp)
    elif len(candles_) == 2:
        candle_set = _timeframe_pair_candles(candles_)
        idx = absindex(index, len(candle_set[0])) + 1
        length = idx - (length + 1)

        return _cross(
            candle_set[0][length:idx], indicator, candle_set[1][length:idx], indicator_cmp
        )

    return False


def _cross(
    candles: List[Candle],
    indicator: str,
    candles_two: List[Candle],
    indicator_cmp: str,
) -> bool:
    if len(candles) != len(candles_two):
        return False

    for i in range(len(candles) - 1, -1, -1):
        reading_one = reading_by_index(candles, indicator, i)
        reading_two = reading_by_index(candles_two, indicator_cmp, i)
        prev_one = reading_by_index(candles, indicator, i - 1)
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
    indicator: str,
    indicator_cmp: str,
    length: int = 1,
    index: int = -1,
) -> bool:
    """Crossover Analysis

    Determines whether the `indicator` reading has crossed over the `indicator_cmp` reading
    within a specified range of candles. A crossover occurs when `indicator` transitions from below
    to above `indicator_cmp` within the given range.

    Args:
        candles (Indicator | Hexital | List[Candle]): The data source containing the indicators.
        indicator (str): The primary indicator to evaluate.
        indicator_cmp (str): The secondary indicator to compare against.
        length (int, optional): The number of candles to include in the range. Defaults to 1.
            If `length` exceeds the total number of candles, all available candles are checked.
        index (int, optional): The index to start the evaluation. Defaults to -1 (latest candle).

    Returns:
        bool: `True` if `indicator` has crossed over `indicator_cmp` within the specified range;
        otherwise `False`.
    """
    candles_ = _retrieve_candles(candles, indicator, indicator_cmp)

    if not candles_:
        return False

    if len(candles_) == 1 and candles_[0]:
        candle_set = candles_[0]
        idx = absindex(index, len(candle_set)) + 1
        length = idx - (length + 1)

        return _crossover(candle_set[length:idx], indicator, candle_set[length:idx], indicator_cmp)
    elif len(candles_) == 2:
        candle_set = _timeframe_pair_candles(candles_)
        idx = absindex(index, len(candle_set[0])) + 1
        length = idx - (length + 1)

        return _crossover(
            candle_set[0][length:idx], indicator, candle_set[1][length:idx], indicator_cmp
        )

    return False


def _crossover(
    candles: List[Candle],
    indicator: str,
    candles_two: List[Candle],
    indicator_cmp: str,
) -> bool:
    if len(candles) != len(candles_two):
        return False

    for i in range(len(candles) - 1, -1, -1):
        reading_one = reading_by_index(candles, indicator, i)
        reading_two = reading_by_index(candles_two, indicator_cmp, i)
        prev_one = reading_by_index(candles, indicator, i - 1)
        prev_two = reading_by_index(candles_two, indicator_cmp, i - 1)

        if None in [reading_one, reading_two, prev_one, prev_two]:
            continue
        elif reading_one > reading_two and prev_one <= prev_two:
            return True

    return False


def crossunder(
    candles: Indicator | Hexital | List[Candle],
    indicator: str,
    indicator_cmp: str,
    length: int = 1,
    index: int = -1,
) -> bool:
    """Crossunder Analysis

    Determines whether the `indicator` reading has crossed under the `indicator_cmp` reading
    within a specified range of candles. A crossunder occurs when `indicator` transitions from above
    to below `indicator_cmp` within the given range.

    Args:
        candles (Indicator | Hexital | List[Candle]): The data source containing the indicators.
        indicator (str): The primary indicator to evaluate.
        indicator_cmp (str): The secondary indicator to compare against.
        length (int, optional): The number of candles to include in the range. Defaults to 1.
            If `length` exceeds the total number of candles, all available candles are checked.
        index (int, optional): The index to start the evaluation. Defaults to -1 (latest candle).

    Returns:
        bool: `True` if `indicator` has crossed under `indicator_cmp` within the specified range;
        otherwise `False`.
    """
    candles_ = _retrieve_candles(candles, indicator, indicator_cmp)

    if not candles_:
        return False

    if len(candles_) == 1 and candles_[0]:
        candle_set = candles_[0]
        idx = absindex(index, len(candle_set)) + 1
        length = idx - (length + 1)

        return _crossunder(
            candle_set[length:idx], indicator, candle_set[length:idx], indicator_cmp
        )
    elif len(candles_) == 2:
        candle_set = _timeframe_pair_candles(candles_)
        idx = absindex(index, len(candle_set[0])) + 1
        length = idx - (length + 1)

        return _crossunder(
            candle_set[0][length:idx], indicator, candle_set[1][length:idx], indicator_cmp
        )

    return False


def _crossunder(
    candles: List[Candle],
    indicator: str,
    candles_two: List[Candle],
    indicator_cmp: str,
) -> bool:
    if len(candles) != len(candles_two):
        return False

    for i in range(len(candles) - 1, -1, -1):
        reading_one = reading_by_index(candles, indicator, i)
        reading_two = reading_by_index(candles_two, indicator_cmp, i)
        prev_one = reading_by_index(candles, indicator, i - 1)
        prev_two = reading_by_index(candles_two, indicator_cmp, i - 1)

        if None in [reading_one, reading_two, prev_one, prev_two]:
            continue
        elif reading_one < reading_two and prev_one >= prev_two:
            return True

    return False


def flipped(
    candles: Indicator | Hexital | List[Candle], indicator: str, length: int = 1, index: int = -1
) -> bool:
    """Flipped Reading Analysis

    Determines whether the `indicator` has "flipped" its value, meaning the current reading is different
    from its previous reading, and within the last `length` candles, the indicator was above its previous reading.

    Args:
        candles (Indicator | Hexital | List[Candle]): The data source containing the indicators.
        indicator (str): The indicator to evaluate.
        length (int, optional): The number of candles to check for a flip. Defaults to 1.
            If `length` exceeds the total number of candles, all available candles are checked.
        index (int, optional): The index to start the evaluation. Defaults to -1 (latest candle).

    Returns:
        bool: `True` if the indicator has flipped (current value differs from previous); otherwise `False`.
    """
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
