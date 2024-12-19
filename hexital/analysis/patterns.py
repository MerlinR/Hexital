from typing import List, Optional

from hexital.analysis import utils
from hexital.core.candle import Candle
from hexital.utils.indexing import absindex


def doji(
    candles: List[Candle],
    lookback: Optional[int] = None,
    index: Optional[int] = None,
) -> bool:
    """Doji Pattern
    A candle body is Doji when it's shorter than 10% of the average of the
    n(10) previous candles' high-low range.

    Source: https://github.com/TA-Lib/ta-lib

    Args:
        candles (Optional[int]): Candles to use to find Doji Candle
        lookback (Optional[int]): Lookback allows detecting an Doji candles N back. Defaults to None.
        index (Optional[int]): Index of Candle to check. Defaults to None/Latest.

    Returns:
        bool: True if given Candle/Candle range is Doji
    """
    index_ = absindex(index, len(candles))

    if lookback is None:
        return _doji(candles, index_)

    return any(_doji(candles, i) for i in range(len(candles) - lookback, len(candles)))


def _doji(candles: List[Candle], index: int):
    if index < 10:
        return False
    return candles[index].realbody < utils.candle_doji(candles, index)


def dojistar(
    candles: List[Candle],
    lookback: Optional[int] = None,
    index: Optional[int] = None,
) -> bool:
    """Dojistar Pattern
    A Dojistar is either bearish or bullish, and is detected when we have a larger then average
    candle followed by a candle candle shorter than 10% of the average of the
    n(10) of the average and then the candle gaps up or down.
    A trend is required to find which direction.

    Source: https://github.com/TA-Lib/ta-lib
    Args:
        candles (Optional[int]): Candles to use to find Dojistar Candle
        lookback (Optional[int]): Lookback allows detecting an Dojistar candles N back. Defaults to None.
        index (Optional[int]): Index of Candle to check. Defaults to None/Latest.

    Returns:
        bool: True if given Candle/Candle range is Doji star
    """
    index_ = absindex(index, len(candles))

    if lookback is None:
        return _dojistar(candles, index_)

    return any(_dojistar(candles, i) for i in range(len(candles) - lookback, len(candles)))


def _dojistar(candles: List[Candle], index: int):
    if index < 10:
        return False
    candle = candles[index]
    prev_candle = candles[index - 1]

    if (
        prev_candle.realbody > utils.candle_bodylong(candles, index - 1)
        and candle.realbody <= utils.candle_doji(candles, index)
        and (
            (prev_candle.positive and utils.realbody_gapup(candle, prev_candle))
            or (prev_candle.negative and utils.realbody_gapdown(candle, prev_candle))
        )
    ):
        return True
    return False


def hammer(
    candles: List[Candle],
    lookback: Optional[int] = None,
    index: Optional[int] = None,
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

    return any(_hammer(candles, i) for i in range(len(candles) - lookback, len(candles)))


def _hammer(candles: List[Candle], index: int):
    if index < 10:
        return False
    candle = candles[index]

    if (
        candle.realbody < utils.candle_bodyshort(candles, index)
        and candle.shadow_lower > utils.candle_shadow_long(candles, index)
        and candle.shadow_upper < utils.candle_shadow_veryshort(candles, index)
        and min(candle.close, candle.open)
        <= candles[index - 1].low + utils.candle_near(candles, index - 1)
    ):
        return True

    return False


def inverted_hammer(
    candles: List[Candle],
    lookback: Optional[int] = None,
    index: Optional[int] = None,
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

    return any(_inverted_hammer(candles, i) for i in range(len(candles) - lookback, len(candles)))


def _inverted_hammer(candles: List[Candle], index: int):
    if index < 10:
        return False
    candle = candles[index]
    prev_candle = candles[index - 1]

    if (
        candle.realbody < utils.candle_bodyshort(candles, index)
        and candle.shadow_upper > utils.candle_shadow_long(candles, index)
        and candle.shadow_lower < utils.candle_shadow_veryshort(candles, index)
        and utils.realbody_gapdown(candle, prev_candle)
    ):
        return True

    return False
