from typing import List, Optional

from hexital.core.candle import Candle


def doji(
    candles: List[Candle],
    length: int = 10,
    lookback: Optional[int] = None,
    asint: bool = False,
    index=None,
) -> bool | int:
    """Doji Pattern
    A candle body is Doji when it's shorter than 10% of the average of the
    n(10) previous candles' high-low range.

    Args:
        candles (List[Candle]): Candles to use to find Doji Candle
        length (int, optional): Check for the average. Defaults to 10.
        lookback (Optional[int], optional): Lookback allows detecting ant Doji candles N back. Defaults to None.
        asint (bool, optional): Use Intergers or Bools. Defaults to False.
        index (_type_, optional): Index of Candle to check. Defaults to None/Latest.

    Returns:
        bool | int: If The given Candle is Doji bool or 1/2
    """
    if len(candles) < length:
        return False
    if index is None:
        index = len(candles) - 1

    def _doji_check(indx: int):
        body = abs(candles[indx].close - candles[indx].open)

        high_low_avg = (
            sum(
                abs(candles[i].high - candles[i].low)
                for i in range(len(candles) - length, len(candles))
            )
            / length
        )
        if asint:
            return 1 if body < 0.13 * high_low_avg else 0
        return body < 0.13 * high_low_avg

    if lookback is None:
        return _doji_check(index)

    return any(_doji_check(i) for i in range(len(candles) - lookback, len(candles)))
