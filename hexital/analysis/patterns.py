from typing import List, Optional

from hexital.analysis import utils
from hexital.core.candle import Candle
from hexital.utils.indexing import validate_index


def doji(
    candles: List[Candle],
    lookback: Optional[int] = None,
    index: Optional[int] = None,
) -> bool:
    """Doji Pattern
    A candle body is Doji when it's shorter than 10% of the average of the
    n(10) previous candles' high-low range.

    Args:
        candles (List[Candle]): Candles to use to find Doji Candle
        length (int, optional): Check for the average. Defaults to 10.
        lookback (Optional[int], optional): Lookback allows detecting ant Doji candles N back. Defaults to None.
        index (_type_, optional): Index of Candle to check. Defaults to None/Latest.

    Returns:
        bool: If The given Candle is Doji bool or 1/2
    """
    index = validate_index(index, len(candles), -1)
    if index is None:
        return False

    def _doji(indx: int):
        if indx < 10:
            return False
        return candles[indx].realbody < utils.candle_doji(candles, indx)

    if lookback is None:
        return _doji(index)

    return any(_doji(i) for i in range(len(candles) - lookback, len(candles)))


def dojistar(
    candles: List[Candle],
    lookback: Optional[int] = None,
    index: Optional[int] = None,
) -> bool:
    index = validate_index(index, len(candles), -1)
    if index is None:
        return False

    def _dojistar(indx: int):
        if indx < 10:
            return False
        candle = candles[indx]
        prev_candle = candles[indx - 1]

        if (
            prev_candle.realbody > utils.candle_bodylong(candles, indx - 1)
            and candle.realbody <= utils.candle_doji(candles, indx)
            and (
                (prev_candle.positive and utils.realbody_gapup(candle, prev_candle))
                or (prev_candle.negative and utils.realbody_gapdown(candle, prev_candle))
            )
        ):
            return True
        return False

    if lookback is None:
        return _dojistar(index)

    return any(_dojistar(i) for i in range(len(candles) - lookback, len(candles)))


def hammer(
    candles: List[Candle],
    lookback: Optional[int] = None,
    index: Optional[int] = None,
) -> bool | int:
    index = validate_index(index, len(candles), -1)
    if index is None:
        return False

    def _hammer(indx: int):
        if indx < 10:
            return False
        candle = candles[indx]

        if (
            candle.realbody < utils.candle_bodyshort(candles, indx)
            and candle.shadow_lower > utils.candle_shadow_long(candles, indx)
            and candle.shadow_upper < utils.candle_shadow_veryshort(candles, indx)
            and min(candle.close, candle.open)
            <= candles[indx - 1].low + utils.candle_near(candles, indx - 1)
        ):
            return True

        return False

    if lookback is None:
        return _hammer(index)

    return any(_hammer(i) for i in range(len(candles) - lookback, len(candles)))


def inverted_hammer(
    candles: List[Candle],
    lookback: Optional[int] = None,
    index: Optional[int] = None,
) -> bool | int:
    index = validate_index(index, len(candles), -1)
    if index is None:
        return False

    def _invhammer(indx: int):
        if indx < 10:
            return False
        candle = candles[indx]
        prev_candle = candles[indx - 1]

        if (
            candle.realbody < utils.candle_bodyshort(candles, indx)
            and candle.shadow_upper > utils.candle_shadow_long(candles, indx)
            and candle.shadow_lower < utils.candle_shadow_veryshort(candles, indx)
            and utils.realbody_gapdown(candle, prev_candle)
        ):
            return True

        return False

    if lookback is None:
        return _invhammer(index)

    return any(_invhammer(i) for i in range(len(candles) - lookback, len(candles)))
