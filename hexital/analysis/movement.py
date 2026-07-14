from ..analysis import utils
from ..core.hexital import Hexital
from ..core.indicator import Indicator
from ..utils.candles import (
    Candle,
    get_readings_period,
    reading_by_index,
)
from ..utils.indexing import absindex, valid_index
from ..utils.timeframe import within_timeframe


def _scalar_reading(
    candle_set: list[Candle],
    indicator: str,
    index: int,
) -> float | int | None:
    reading = reading_by_index(candle_set, indicator, index)
    if isinstance(reading, dict) or reading is None:
        return None
    return reading


def _retrieve_candles(
    obj: Indicator | Hexital | list[Candle],
    indicator: str | None = None,
    indicator_cmp: str | None = None,
) -> list[Candle] | tuple[list[Candle], list[Candle]]:
    if isinstance(obj, list):
        return obj
    if isinstance(obj, Indicator):
        return obj.candles
    if isinstance(obj, Hexital) and not indicator and not indicator_cmp:
        return obj.candles()
    if isinstance(obj, Hexital) and indicator:
        pairing = obj.find_candle_pairing(indicator, indicator_cmp)
        if not indicator_cmp:
            return pairing[0]
        return pairing

    return []


def _timeframe_pair_candles(
    candles: tuple[list[Candle], list[Candle]],
) -> tuple[list[Candle], list[Candle]]:
    output_one, output_two = [], []
    set_one, set_two = candles

    if set_one[-1].timeframe == set_two[-1].timeframe:
        return candles
    end_pointer = len(candles[1]) - 1

    for front_pointer in range(len(set_one) - 1, -1, -1):
        if end_pointer < 0:
            break

        ts_one = set_one[front_pointer].timestamp
        if ts_one is None:
            continue

        while end_pointer >= 0:
            ts_two = set_two[end_pointer].timestamp
            if ts_two is None:
                end_pointer -= 1
                continue

            if within_timeframe(
                ts_one,
                ts_two,
                set_two[end_pointer].timeframe,
            ) or within_timeframe(
                ts_two,
                ts_one,
                set_one[front_pointer].timeframe,
            ):
                break

            end_pointer -= 1

        if end_pointer >= 0:
            output_one.append(set_one[front_pointer])
            output_two.append(set_two[end_pointer])

    output_one.reverse()
    output_two.reverse()
    return output_one, output_two


def positive(candles: Candle | list[Candle], index: int = -1) -> bool:
    if isinstance(candles, Candle):
        return candles.positive

    if not valid_index(index, len(candles)):
        return False
    return candles[index].positive


def negative(candles: Candle | list[Candle], index: int = -1) -> bool:
    if isinstance(candles, Candle):
        return candles.negative

    if not valid_index(index, len(candles)):
        return False
    return candles[index].negative


def above(
    candles: Indicator | Hexital | list[Candle],
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

    if isinstance(candles_, list):
        idx = absindex(index, len(candles_)) + 1
        length = idx - (length + 1)

        return _above(
            candles_[length:idx],
            indicator,
            candles_[length:idx],
            indicator_cmp,
        )
    if isinstance(candles_, tuple):
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
    candles: list[Candle],
    indicator: str,
    candles_two: list[Candle],
    indicator_cmp: str,
) -> bool:
    if len(candles) != len(candles_two):
        return False

    for i in range(len(candles)):
        reading_one = reading_by_index(candles, indicator, i)
        reading_two = reading_by_index(candles_two, indicator_cmp, i)

        if (
            isinstance(reading_one, (float, int))
            and isinstance(reading_two, (float, int))
            and reading_one > reading_two
        ):
            return True

    return False


def below(
    candles: Indicator | Hexital | list[Candle],
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

    if isinstance(candles_, list):
        idx = absindex(index, len(candles_)) + 1
        length = idx - (length + 1)

        return _below(
            candles_[length:idx],
            indicator,
            candles_[length:idx],
            indicator_cmp,
        )
    if isinstance(candles_, tuple):
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
    candles: list[Candle],
    indicator: str,
    candles_two: list[Candle],
    indicator_cmp: str,
) -> bool:
    if len(candles) != len(candles_two):
        return False

    for i in range(len(candles)):
        reading_one = reading_by_index(candles, indicator, i)
        reading_two = reading_by_index(candles_two, indicator_cmp, i)

        if (
            isinstance(reading_one, (float, int))
            and isinstance(reading_two, (float, int))
            and reading_one < reading_two
        ):
            return True

    return False


def value_range(
    candles: Indicator | Hexital | list[Candle],
    indicator: str,
    length: int = 4,
    index: int = -1,
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
    candle_set = _retrieve_candles(candles, indicator)
    if not isinstance(candle_set, list) or not candle_set:
        return None

    readings = get_readings_period(candle_set, indicator, length, index, True)

    if len(readings) < 2:
        return None

    return abs(min(readings) - max(readings))


def bars_since(
    candles: Indicator | Hexital | list[Candle],
    indicator: str,
    value: float | int | bool = True,
    index: int = -1,
) -> int | None:
    """Bars Since Analysis

    Returns how many bars ago the given `indicator` last matched `value`.
    A return value of `0` means the current bar matches. If no match exists,
    returns `None`.

    Args:
        candles (Indicator | Hexital | List[Candle]): The data source containing the indicators.
        indicator (str): The indicator series to scan.
        value (float | int | bool, optional): The value to match against. Defaults to `True`.
        index (int, optional): The index to start the backward scan from.
            Defaults to -1 (latest candle).

    Returns:
        int | None: The number of bars since the most recent matching value,
        or `None` if no matching value exists.
    """
    candle_set = _retrieve_candles(candles, indicator)
    if not isinstance(candle_set, list) or not candle_set:
        return None

    idx = absindex(index, len(candle_set))

    for offset, candle_idx in enumerate(range(idx, -1, -1)):
        if reading_by_index(candle_set, indicator, candle_idx) == value:
            return offset

    return None


def value_when(
    candles: Indicator | Hexital | list[Candle],
    condition_indicator: str,
    indicator: str,
    value: float | int | bool = True,
    occurrence: int = 0,
    index: int = -1,
) -> float | dict | None:
    """Value When Analysis

    Returns the `indicator` reading from the nth most recent bar where
    `condition_indicator` matched `value`. `occurrence=0` means the latest match.

    Args:
        candles (Indicator | Hexital | List[Candle]): The data source containing the indicators.
        condition_indicator (str): The indicator series used as the condition.
        indicator (str): The indicator reading to return when the condition matches.
        value (float | int | bool, optional): The value the condition indicator must equal.
            Defaults to `True`.
        occurrence (int, optional): Which matching occurrence to return, where `0` is the
            latest match. Defaults to 0.
        index (int, optional): The index to start the backward scan from.
            Defaults to -1 (latest candle).

    Returns:
        float | dict | None: The reading of `indicator` at the requested matching occurrence,
        or `None` if no such match exists.
    """
    candle_set = _retrieve_candles(candles, condition_indicator)
    if not isinstance(candle_set, list) or not candle_set or occurrence < 0:
        return None

    idx = absindex(index, len(candle_set))
    found = 0

    for candle_idx in range(idx, -1, -1):
        if reading_by_index(candle_set, condition_indicator, candle_idx) != value:
            continue

        if found == occurrence:
            return reading_by_index(candle_set, indicator, candle_idx)

        found += 1

    return None


def change(
    candles: Indicator | Hexital | list[Candle],
    indicator: str,
    length: int = 1,
    index: int = -1,
) -> float | int | None:
    """Change Analysis

    Returns the difference between the current reading and the reading
    `length` bars back.

    Args:
        candles (Indicator | Hexital | List[Candle]): The data source containing the indicators.
        indicator (str): The indicator series to compare.
        length (int, optional): How many bars back to compare against. Defaults to 1.
        index (int, optional): The index to evaluate from. Defaults to -1 (latest candle).

    Returns:
        float | int | None: The current reading minus the reading `length` bars back,
        or `None` if there is insufficient valid data.
    """
    candle_set = _retrieve_candles(candles, indicator)
    if not isinstance(candle_set, list) or not candle_set or length < 1:
        return None

    idx = absindex(index, len(candle_set))
    current = _scalar_reading(candle_set, indicator, idx)
    previous = _scalar_reading(candle_set, indicator, idx - length)

    if current is None or previous is None:
        return None

    return current - previous


def percent_change(
    candles: Indicator | Hexital | list[Candle],
    indicator: str,
    length: int = 1,
    index: int = -1,
) -> float | None:
    """Percent Change Analysis

    Returns the percentage change between the current reading and the reading
    `length` bars back.

    Args:
        candles (Indicator | Hexital | List[Candle]): The data source containing the indicators.
        indicator (str): The indicator series to compare.
        length (int, optional): How many bars back to compare against. Defaults to 1.
        index (int, optional): The index to evaluate from. Defaults to -1 (latest candle).

    Returns:
        float | None: The percentage change from the reading `length` bars back to the
        current reading, or `None` if there is insufficient valid data or the prior value is zero.
    """
    delta = change(candles, indicator, length, index)
    if delta is None:
        return None

    candle_set = _retrieve_candles(candles, indicator)
    if not isinstance(candle_set, list) or not candle_set:
        return None

    idx = absindex(index, len(candle_set))
    previous = _scalar_reading(candle_set, indicator, idx - length)

    if previous in (None, 0):
        return None

    return (delta / previous) * 100


def rising_count(
    candles: Indicator | Hexital | list[Candle],
    indicator: str,
    length: int = 100,
    index: int = -1,
) -> int:
    """Rising Count Analysis

    Counts consecutive rising bars ending at `index`, up to `length`
    comparisons back.

    Args:
        candles (Indicator | Hexital | List[Candle]): The data source containing the indicators.
        indicator (str): The indicator series to evaluate.
        length (int, optional): Maximum number of backward comparisons to check.
            Defaults to 100.
        index (int, optional): The index to evaluate from. Defaults to -1 (latest candle).

    Returns:
        int: The number of consecutive rising comparisons ending at `index`.
    """
    candle_set = _retrieve_candles(candles, indicator)
    if not isinstance(candle_set, list) or not candle_set or length < 1:
        return 0

    idx = absindex(index, len(candle_set))
    count = 0

    for candle_idx in range(idx, idx - length, -1):
        current = _scalar_reading(candle_set, indicator, candle_idx)
        previous = _scalar_reading(candle_set, indicator, candle_idx - 1)

        if current is None or previous is None or current <= previous:
            break

        count += 1

    return count


def falling_count(
    candles: Indicator | Hexital | list[Candle],
    indicator: str,
    length: int = 100,
    index: int = -1,
) -> int:
    """Falling Count Analysis

    Counts consecutive falling bars ending at `index`, up to `length`
    comparisons back.

    Args:
        candles (Indicator | Hexital | List[Candle]): The data source containing the indicators.
        indicator (str): The indicator series to evaluate.
        length (int, optional): Maximum number of backward comparisons to check.
            Defaults to 100.
        index (int, optional): The index to evaluate from. Defaults to -1 (latest candle).

    Returns:
        int: The number of consecutive falling comparisons ending at `index`.
    """
    candle_set = _retrieve_candles(candles, indicator)
    if not isinstance(candle_set, list) or not candle_set or length < 1:
        return 0

    idx = absindex(index, len(candle_set))
    count = 0

    for candle_idx in range(idx, idx - length, -1):
        current = _scalar_reading(candle_set, indicator, candle_idx)
        previous = _scalar_reading(candle_set, indicator, candle_idx - 1)

        if current is None or previous is None or current >= previous:
            break

        count += 1

    return count


def rising(
    candles: Indicator | Hexital | list[Candle],
    indicator: str,
    length: int = 1,
    index: int = -1,
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
    candle_set = _retrieve_candles(candles, indicator)
    if (
        not isinstance(candle_set, list)
        or not candle_set
        or length < 1
        or len(candle_set) < 2
    ):
        return False

    idx = absindex(index, len(candle_set))

    latest_reading = _scalar_reading(candle_set, indicator, idx)
    if latest_reading is None:
        return False

    readings = get_readings_period(candle_set, indicator, length, idx)
    if not readings:
        return False

    return all(reading < latest_reading for reading in readings)


def falling(
    candles: Indicator | Hexital | list[Candle],
    indicator: str,
    length: int = 1,
    index: int = -1,
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
    candle_set = _retrieve_candles(candles, indicator)
    if (
        not isinstance(candle_set, list)
        or not candle_set
        or length < 1
        or len(candle_set) < 2
    ):
        return False

    idx = absindex(index, len(candle_set))

    latest_reading = _scalar_reading(candle_set, indicator, idx)
    if latest_reading is None:
        return False

    readings = get_readings_period(candle_set, indicator, length, idx)
    if not readings:
        return False

    return all(reading > latest_reading for reading in readings)


def mean_rising(
    candles: Indicator | Hexital | list[Candle],
    indicator: str,
    length: int = 4,
    index: int = -1,
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

    candle_set = _retrieve_candles(candles, indicator)
    if (
        not isinstance(candle_set, list)
        or not candle_set
        or length < 1
        or len(candle_set) < 2
    ):
        return False

    idx = absindex(index, len(candle_set))

    latest_reading = _scalar_reading(candle_set, indicator, idx)
    if latest_reading is None:
        return False

    readings = get_readings_period(candle_set, indicator, length, idx)
    if not readings:
        return False

    return sum(readings) / len(readings) < latest_reading


def mean_falling(
    candles: Indicator | Hexital | list[Candle],
    indicator: str,
    length: int = 4,
    index: int = -1,
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
    candle_set = _retrieve_candles(candles, indicator)
    if (
        not isinstance(candle_set, list)
        or not candle_set
        or length < 1
        or len(candle_set) < 2
    ):
        return False

    idx = absindex(index, len(candle_set))

    latest_reading = _scalar_reading(candle_set, indicator, idx)
    if latest_reading is None:
        return False

    readings = get_readings_period(candle_set, indicator, length, idx)
    if not readings:
        return False

    return sum(readings) / len(readings) > latest_reading


def highest(
    candles: Indicator | Hexital | list[Candle],
    indicator: str,
    length: int = 4,
    index: int = -1,
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
    candles_ = _retrieve_candles(candles, indicator)
    if not isinstance(candles_, list):
        return None
    return utils.highest(candles_, indicator, length, index)


def lowest(
    candles: Indicator | Hexital | list[Candle],
    indicator: str,
    length: int = 4,
    index: int = -1,
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
    candles_ = _retrieve_candles(candles, indicator)
    if not isinstance(candles_, list):
        return None
    return utils.lowest(candles_, indicator, length, index)


def highestbar(
    candles: Indicator | Hexital | list[Candle],
    indicator: str,
    length: int = 4,
    index: int = -1,
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
    candle_set = _retrieve_candles(candles, indicator)
    if not isinstance(candle_set, list) or not candle_set:
        return None

    idx = absindex(index, len(candle_set))

    high = None
    distance = 0

    for offset, candle_idx in enumerate(range(idx, idx - length, -1)):
        current = _scalar_reading(candle_set, indicator, candle_idx)
        if current is None:
            continue

        if high is None or high < current:
            high = current
            distance = offset

    return distance


def lowestbar(
    candles: Indicator | Hexital | list[Candle],
    indicator: str,
    length: int = 4,
    index: int = -1,
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
    candle_set = _retrieve_candles(candles, indicator)
    if not isinstance(candle_set, list) or not candle_set:
        return None

    idx = absindex(index, len(candle_set))

    low = None
    distance = 0

    for offset, candle_idx in enumerate(range(idx, idx - length, -1)):
        current = _scalar_reading(candle_set, indicator, candle_idx)
        if current is None:
            continue

        if low is None or low > current:
            low = current
            distance = offset

    return distance


def cross(
    candles: Indicator | Hexital | list[Candle],
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

    if isinstance(candles_, list):
        idx = absindex(index, len(candles_)) + 1
        length = idx - (length + 1)
        return _cross(
            candles_[length:idx], indicator, candles_[length:idx], indicator_cmp
        )

    if isinstance(candles_, tuple):
        candle_set = _timeframe_pair_candles(candles_)
        idx = absindex(index, len(candle_set[0])) + 1
        length = idx - (length + 1)
        return _cross(
            candle_set[0][length:idx],
            indicator,
            candle_set[1][length:idx],
            indicator_cmp,
        )

    return False


def _cross(
    candles: list[Candle],
    indicator: str,
    candles_two: list[Candle],
    indicator_cmp: str,
) -> bool:
    if len(candles) != len(candles_two):
        return False

    for i in range(len(candles) - 1, -1, -1):
        reading_one = reading_by_index(candles, indicator, i)
        reading_two = reading_by_index(candles_two, indicator_cmp, i)
        prev_one = reading_by_index(candles, indicator, i - 1)
        prev_two = reading_by_index(candles_two, indicator_cmp, i - 1)

        if not all(
            isinstance(r, (float, int))
            for r in [reading_one, reading_two, prev_one, prev_two]
        ):
            continue
        if (reading_one < reading_two and prev_one >= prev_two) or (
            reading_one > reading_two and prev_one <= prev_two
        ):
            return True

    return False


def crossover(
    candles: Indicator | Hexital | list[Candle],
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

    if isinstance(candles_, list):
        idx = absindex(index, len(candles_)) + 1
        length = idx - (length + 1)
        return _crossover(
            candles_[length:idx], indicator, candles_[length:idx], indicator_cmp
        )

    if isinstance(candles_, tuple):
        candle_set = _timeframe_pair_candles(candles_)
        idx = absindex(index, len(candle_set[0])) + 1
        length = idx - (length + 1)

        return _crossover(
            candle_set[0][length:idx],
            indicator,
            candle_set[1][length:idx],
            indicator_cmp,
        )

    return False


def _crossover(
    candles: list[Candle],
    indicator: str,
    candles_two: list[Candle],
    indicator_cmp: str,
) -> bool:
    if len(candles) != len(candles_two):
        return False

    for i in range(len(candles) - 1, -1, -1):
        reading_one = reading_by_index(candles, indicator, i)
        reading_two = reading_by_index(candles_two, indicator_cmp, i)
        prev_one = reading_by_index(candles, indicator, i - 1)
        prev_two = reading_by_index(candles_two, indicator_cmp, i - 1)

        if not all(
            isinstance(r, (float, int))
            for r in [reading_one, reading_two, prev_one, prev_two]
        ):
            continue
        if reading_one > reading_two and prev_one <= prev_two:
            return True

    return False


def crossunder(
    candles: Indicator | Hexital | list[Candle],
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

    if isinstance(candles_, list):
        idx = absindex(index, len(candles_)) + 1
        length = idx - (length + 1)
        return _crossunder(
            candles_[length:idx], indicator, candles_[length:idx], indicator_cmp
        )

    if isinstance(candles_, tuple):
        candle_set = _timeframe_pair_candles(candles_)
        idx = absindex(index, len(candle_set[0])) + 1
        length = idx - (length + 1)

        return _crossunder(
            candle_set[0][length:idx],
            indicator,
            candle_set[1][length:idx],
            indicator_cmp,
        )

    return False


def _crossunder(
    candles: list[Candle],
    indicator: str,
    candles_two: list[Candle],
    indicator_cmp: str,
) -> bool:
    if len(candles) != len(candles_two):
        return False

    for i in range(len(candles) - 1, -1, -1):
        reading_one = reading_by_index(candles, indicator, i)
        reading_two = reading_by_index(candles_two, indicator_cmp, i)
        prev_one = reading_by_index(candles, indicator, i - 1)
        prev_two = reading_by_index(candles_two, indicator_cmp, i - 1)

        if not all(
            isinstance(r, (float, int))
            for r in [reading_one, reading_two, prev_one, prev_two]
        ):
            continue
        if reading_one < reading_two and prev_one >= prev_two:
            return True

    return False


def flipped(
    candles: Indicator | Hexital | list[Candle],
    indicator: str,
    length: int = 1,
    index: int = -1,
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
    candle_set = _retrieve_candles(candles, indicator)
    if not isinstance(candle_set, list) or not candle_set:
        return False

    idx = absindex(index, len(candle_set))

    for idx in range(idx, idx - length, -1):
        if reading_by_index(candle_set, indicator, idx) != reading_by_index(
            candle_set, indicator, idx - 1
        ):
            return True

    return False
