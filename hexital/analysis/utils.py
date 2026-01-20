from hexital.core.candle import Candle
from hexital.utils.candles import get_readings_period
from hexital.utils.indexing import absindex


def highest(
    candles: list[Candle], name: str, length: int, index: int | None = None
) -> float | None:
    """
    Computes the highest value of the specified `name` over a given range of candles.
    The range includes the latest candle by default and considers up to the specified number of candles.
    """
    if not candles:
        return None

    readings = get_readings_period(
        candles, name, length, absindex(index, len(candles)), True
    )
    return max(readings, default=None)


def lowest(
    candles: list[Candle], name: str, length: int, index: int | None = None
) -> float | None:
    """
    Computes the lowest value of the specified `indicator` over a given range of candles.
    The range includes the latest candle by default and considers up to the specified number of candles.
    """
    if not candles:
        return None

    readings = get_readings_period(
        candles, name, length, absindex(index, len(candles)), True
    )
    return min(readings, default=None)


def realbody_avg(candles: list[Candle], length: int, index: int | None = None) -> float:
    """
    Computes the average real body of a specified number of candles, including the current candle.
    The real body is calculated as the absolute difference between a candle's open and close prices.
    """
    index = absindex(index, len(candles)) + 1
    start_index = max(0, index - length)
    actual_length = index - start_index

    return sum(candles[i].realbody for i in range(start_index, index)) / actual_length


def high_low_avg(candles: list[Candle], length: int, index: int | None = None) -> float:
    """
    Computes the average of the high-low range over a specified number of candles,
    including the current candle. The high-low range is the difference between a candle's
    high and low prices.
    """
    index = absindex(index, len(candles)) + 1
    start_index = max(0, index - length)
    actual_length = index - start_index

    return sum(candles[i].high_low for i in range(start_index, index)) / actual_length


def shadow_upper_avg(
    candles: list[Candle], length: int, index: int | None = None
) -> float:
    """
    Computes the average upper shadow over a specified number of candles, including the current candle.
    The upper shadow is the difference between a candle's high price and either its open or close price.
    """
    index = absindex(index, len(candles)) + 1
    start_index = max(0, index - length)
    actual_length = index - start_index

    return sum(candles[i].shadow_upper for i in range(start_index, index)) / actual_length


def shadow_lower_avg(
    candles: list[Candle], length: int, index: int | None = None
) -> float:
    """
    Computes the average lower shadow over a specified number of candles, including the current candle.
    The lower shadow is the difference between a candle's high price and either its open or close price.
    """
    index = absindex(index, len(candles)) + 1
    start_index = max(0, index - length)
    actual_length = index - start_index

    return sum(candles[i].shadow_lower for i in range(start_index, index)) / actual_length


def realbody_gapup(candle: Candle, candle_two: Candle) -> bool:
    """
    Computes if a candle has a real body gap-up compared to a previous candle.
    A gap-up occurs when the minimum value of the current candle's real body
    (i.e., the lower of its open or close) is greater than the maximum value
    of the previous candle's real body (i.e., the higher of its open or close).
    """
    return min(candle.open, candle.close) > max(candle_two.open, candle_two.close)


def realbody_gapdown(candle: Candle, candle_two: Candle) -> bool:
    """
    Computes if a candle has a real body gap-down compared to a previous candle.
    A gap-down occurs when the maximum value of the current candle's real body
    (i.e., the higher of its open or close) is less than the minimum value
    of the previous candle's real body (i.e., the lower of its open or close).
    """
    return max(candle.open, candle.close) < min(candle_two.open, candle_two.close)


def candle_gapup(candle: Candle, candle_two: Candle) -> bool:
    return candle.low > candle_two.high


def candle_gapdown(candle: Candle, candle_two: Candle) -> bool:
    return candle.high < candle_two.low


# Below are TA-lib globally used utils
# https://github.com/TA-Lib/ta-lib/blob/main/src/ta_common/ta_global.c


def _realbody_percentage(
    candles: list[Candle],
    index: int | None = None,
    percentage: float = 1.0,
    length: int = 10,
) -> float:
    return realbody_avg(candles, length, absindex(index, len(candles))) * percentage


def _high_low_percentage(
    candles: list[Candle],
    index: int | None = None,
    percentage: float = 1.0,
    length: int = 10,
) -> float:
    return high_low_avg(candles, length, absindex(index, len(candles))) * percentage


def candle_bodydoji(
    candles: list[Candle], index: int | None = None, length: int = 10
) -> float:
    """A real body is like doji's body when it's shorter than 10% the average of the 10 previous candles' high-low range

    Returns:
        float: 10% of the average of the 'length' previous candles' high-low range
    """
    return _high_low_percentage(candles, index=index, length=length, percentage=0.1)


def candle_bodylong(
    candles: list[Candle], index: int | None = None, length: int = 10
) -> float:
    """A real body is long when it's longer than the average of the 10 previous candles' real body

    Returns:
        float: Average of the 'length' previous candles' real body"""
    return _realbody_percentage(candles, index=index, length=length)


def candle_bodyverylong(
    candles: list[Candle], index: int | None = None, length: int = 10
) -> float:
    """A real body is very long when it's longer than 3 times the average of the 10 previous candles' real body

    Returns:
        float: Average of the 'length' previous candles' real body multiplied by 3"""
    return _realbody_percentage(candles, index=index, length=length, percentage=3)


def candle_bodyshort(
    candles: list[Candle], index: int | None = None, length: int = 10
) -> float:
    """real body is short when it's shorter than the average of the 10 previous candles' real bodies

    Returns:
        float: Average of the 'length' previous candles' real body"""
    return _realbody_percentage(candles, index=index, length=length)


def candle_shadow_short(
    candles: list[Candle], index: int | None = None, length: int = 10
) -> float:
    """shadow is short when it's shorter than half the average of the 10 previous candles' sum of shadows

    Returns:
        float: Average of the 'length' previous candles' high-low range"""
    return _high_low_percentage(candles, index=index, length=length)


def candle_shadow_veryshort(
    candles: list[Candle], index: int | None = None, length: int = 10
) -> float:
    """shadow is very short when it's shorter than 10% the average of the 10 previous candles' high-low range

    Returns:
        float: 10% the average of the 'length' previous candles' high-low range"""
    return _high_low_percentage(candles, index=index, length=length, percentage=0.1)


def candle_shadow_long(candles: list[Candle], index: int | None = None) -> float:
    """shadow is long when it's longer than the real body

    Returns:
        float: Candle's realbody"""
    return candles[index if index is not None else -1].realbody


def candle_shadow_verylong(candles: list[Candle], index: int | None = None) -> float:
    """shadow is very long when it's longer than 2 times the real body

    Returns:
        float: Candle's realbody multiplied by 2"""
    return candles[index if index is not None else -1].realbody * 2


def candle_equal(
    candles: list[Candle], index: int | None = None, length: int = 5
) -> float:
    """when measuring distance between parts of candles or width of gaps
    equal means "<= 5% of the average of the 5 previous candles' high-low range

    Returns:
        float: 5% the average of the 'length' previous candles' high-low range"""
    return _high_low_percentage(candles, index=index, length=length, percentage=0.05)


def candle_near(
    candles: list[Candle], index: int | None = None, length: int = 5
) -> float:
    """when measuring distance between parts of candles or width of gaps
    near means "<= 20% of the average of the 5 previous candles' high-low range"

    Returns:
        float: 20% the average of the 'length' previous candles' high-low range"""
    return _high_low_percentage(candles, index=index, length=length, percentage=0.2)


def candle_far(candles: list[Candle], index: int | None = None, length: int = 5) -> float:
    """when measuring distance between parts of candles or width of gaps
    far means ">= 60% of the average of the 5 previous candles' high-low range

    Returns:
        float: 60% the average of the 'length' previous candles' high-low range"""
    return _high_low_percentage(candles, index=index, length=length, percentage=0.6)
