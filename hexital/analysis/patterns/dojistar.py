from ...core.candle import Candle
from ...utils.indexing import absindex
from .. import utils


def dojistar(
    candles: list[Candle],
    lookback: int | None = None,
    index: int | None = None,
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

    return any(_dojistar(candles, i) for i in utils.lookback_range(index_, lookback))


def _dojistar(candles: list[Candle], index: int):
    if index < 10:
        return False
    candle = candles[index]
    prev_candle = candles[index - 1]

    return (
        prev_candle.realbody > utils.candle_bodylong(candles, index - 1)
        and candle.realbody <= utils.candle_bodydoji(candles, index)
        and (
            (prev_candle.positive and utils.realbody_gapup(candle, prev_candle))
            or (prev_candle.negative and utils.realbody_gapdown(candle, prev_candle))
        )
    )
