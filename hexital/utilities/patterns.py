from typing import List

from hexital.types.ohlcv import OHLCV


def doji(candles: List[OHLCV], length: int = 10, percent: int = 10) -> bool:
    """A candle body is Doji, when it's shorter than 10% of the
    average of the 10 previous candles' high-low range."""
    if len(candles) < length:
        return False
    if not 0 <= percent <= 100:
        percent = 10
    return False
