from ...core.candle import Candle
from ...utils.indexing import absindex
from .. import utils


def doji(
    candles: list[Candle],
    lookback: int | None = None,
    index: int | None = None,
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

    return any(_doji(candles, i) for i in utils.lookback_range(index_, lookback))


def _doji(candles: list[Candle], index: int):
    if index < 10:
        return False
    return candles[index].realbody < utils.candle_bodydoji(candles, index)
