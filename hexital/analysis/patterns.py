from typing import List, Optional

from hexital.analysis import utils
from hexital.core.candle import Candle
from hexital.utils.indexing import validate_index


def doji(
    candles: List[Candle],
    length: int = 10,
    lookback: Optional[int] = None,
    asint: bool = False,
    index: Optional[int] = None,
) -> bool | int:
    """Doji Pattern
    A candle body is Doji when it's shorter than 10% of the average of the
    n(10) previous candles' high-low range.

    Args:
        candles (List[Candle]): Candles to use to find Doji Candle
        length (int, optional): Check for the average. Defaults to 10.
        lookback (Optional[int], optional): Lookback allows detecting ant Doji candles N back. Defaults to None.
        asint (bool, optional): Use Integers or Bools. Defaults to False.
        index (_type_, optional): Index of Candle to check. Defaults to None/Latest.

    Returns:
        bool | int: If The given Candle is Doji bool or 1/2
    """
    index = validate_index(index, len(candles), -1)
    if index is None:
        return False

    def _doji(indx: int):
        body = candles[indx].realbody()

        high_low_avg = utils.high_low_avg(candles, length, indx)

        is_doji = body < 0.1 * high_low_avg
        return int(is_doji) if asint else is_doji

    if lookback is None:
        return _doji(index)

    return any(_doji(i) for i in range(len(candles) - lookback, len(candles)))


def hammer(
    candles: List[Candle],
    length: int = 10,
    lookback: Optional[int] = None,
    asint: bool = False,
    index: Optional[int] = None,
) -> bool | int:
    index = validate_index(index, len(candles), -1)
    if index is None:
        return False

    def _hammer(indx: int):
        is_hammer = False

        body = candles[indx].realbody()
        body_middle = candles[indx].high - candles[indx].low

        body_average = utils.realbody_avg(candles, length, indx)

        upper_shadow_avg = utils.shadow_upper_avg(candles, length, indx)
        lower_shadow_avg = utils.shadow_lower_avg(candles, length, indx)

        if (
            body < body_average
            and candles[indx].shadow_lower() > lower_shadow_avg
            and candles[indx].shadow_lower() < upper_shadow_avg
            and abs(body_middle - candles[indx - 1].low) < 10
        ):
            is_hammer = True

        return int(is_hammer) if asint else is_hammer

    if lookback is None:
        return _hammer(index)

    return any(_hammer(i) for i in range(len(candles) - lookback, len(candles)))
