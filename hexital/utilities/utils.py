from typing import Dict, List, Optional

from hexital.types.ohlcv import OHLCV
from hexital.utilities.ohlcv import reading_by_candle


def candles_sum(
    candles: List[OHLCV], indicator: str, length: int = 1, index: Optional[int] = None
) -> float:
    """Sum of `indicator` for `length` bars back. including index/latest"""

    if (index is not None and index >= len(candles)) or index is None:
        index = len(candles)
    elif index is not None and index >= 0:
        index += 1
    elif index is not None:
        index = (index * -1) + 1

    if length > len(candles):
        length = len(candles)

    return sum(
        reading_by_candle(candle, indicator)
        for candle in candles[index - length : index]
        if reading_by_candle(candle, indicator) is not None
    )


def round_values(
    value: float | Dict[str, float], round_by: int = 4
) -> float | Dict[str, float]:
    if isinstance(value, float):
        return round(value, round_by)

    if isinstance(value, dict):
        for key, val in value.items():
            if isinstance(val, float):
                value[key] = round(val, round_by)

    return value
