from typing import List

from hexital.types.ohlcv import OHLCV
from hexital.utilities.ohlcv import reading_by_candle, reading_period


def candles_sum(
    candles: List[OHLCV], indicator: str, length: int = 1, index: int = None
) -> float:
    """Sum of `indicator` for `length` bars back. including index/latest"""
    if not reading_period(candles, length, indicator):
        length = len(candles)

    if index is not None and index >= len(candles):
        index = len(candles)
    elif index is not None and index >= 0:
        index += 1
    elif index is not None:
        index = (index * -1) + 1
    else:
        index = len(candles)

    return sum(
        reading_by_candle(candle, indicator)
        for candle in candles[index - length : index]
    )
