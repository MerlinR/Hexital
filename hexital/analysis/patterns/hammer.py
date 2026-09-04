from ...core.candle import Candle
from ...utils.indexing import absindex
from .. import utils


def hammer(
    candles: list[Candle],
    lookback: int | None = None,
    index: int | None = None,
) -> bool | int:
    """Hammer Pattern
    A Hammer is detected when the Candle's open and close values are considered shorter
    than 10% of the average of the n(10) candles. However the low is larger than the average.

    Source: https://github.com/TA-Lib/ta-lib
    Args:
        candles (Optional[int]): Candles to use to find Hammer Candle
        lookback (Optional[int]): Lookback allows detecting an Hammer candles N back. Defaults to None.
        index (Optional[int]): Index of Candle to check. Defaults to None/Latest.

    Returns:
        bool: True if given Candle/Candle range is Hammer
    """
    index_ = absindex(index, len(candles))

    if lookback is None:
        return _hammer(candles, index_)

    return any(_hammer(candles, i) for i in utils.lookback_range(index_, lookback))


def _hammer(candles: list[Candle], index: int):
    if index < 10:
        return False
    candle = candles[index]

    return (
        candle.realbody < utils.candle_bodyshort(candles, index)
        and candle.shadow_lower > utils.candle_shadow_long(candles, index)
        and candle.shadow_upper < utils.candle_shadow_veryshort(candles, index)
        and min(candle.close, candle.open)
        <= candles[index - 1].low + utils.candle_near(candles, index - 1)
    )


def inverted_hammer(
    candles: list[Candle],
    lookback: int | None = None,
    index: int | None = None,
) -> bool | int:
    """Inverted Hammer Pattern
    An Inverted Hammer is detected when the Candle's open and close values are considered shorter
    than 10% of the average of the n(10) candles. However the high is larger than the average.

    Source: https://github.com/TA-Lib/ta-lib
    Args:
        candles (Optional[int]): Candles to use to find Inverted Hammer Candle
        lookback (Optional[int]): Lookback allows detecting an InvertedHammer candles N back. Defaults to None.
        index (Optional[int]): Index of Candle to check. Defaults to None/Latest.

    Returns:
        bool: True if given Candle/Candle range is Inverted Hammer
    """
    index_ = absindex(index, len(candles))

    if lookback is None:
        return _inverted_hammer(candles, index_)

    return any(
        _inverted_hammer(candles, i) for i in utils.lookback_range(index_, lookback)
    )


def _inverted_hammer(candles: list[Candle], index: int):
    if index < 10:
        return False
    candle = candles[index]
    prev_candle = candles[index - 1]

    return (
        candle.realbody < utils.candle_bodyshort(candles, index)
        and candle.shadow_upper > utils.candle_shadow_long(candles, index)
        and candle.shadow_lower < utils.candle_shadow_veryshort(candles, index)
        and utils.realbody_gapdown(candle, prev_candle)
    )
