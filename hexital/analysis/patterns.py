from typing import List, Optional

from hexital.core.ohlcv import OHLCV


def doji(candles: List[OHLCV], length: int = 10, lookback: Optional[int] = None) -> bool:
    """A candle body is Doji.
    when it's shorter than 10% of theaverage of the 10 previous candles' high-low range.
    Lookback allows detecting ant Doji candles N back"""

    def _doji_check(index: int):
        body = abs(candles[index].close - candles[index].open)
        hl_avg = (
            sum(
                abs(candles[i].high - candles[i].low)
                for i in range(len(candles) - length, len(candles))
            )
            / length
        )

        return body < hl_avg * 0.1

    if len(candles) < length:
        return False

    if lookback is None:
        return _doji_check(-1)

    return any(_doji_check(i) for i in range(len(candles) - lookback, len(candles)))
