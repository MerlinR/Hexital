from ...core.candle import Candle
from ...utils.indexing import absindex
from .. import utils


def bullish_harami(
    candles: list[Candle],
    lookback: int | None = None,
    index: int | None = None,
) -> bool:
    """Bullish Harami Pattern

    A bullish harami forms when a long bearish candle is followed by a short
    candle whose real body lies strictly inside the prior body.

    Source: https://github.com/TA-Lib/ta-lib

    Args:
        candles: Candle series to evaluate.
        lookback: When set, scan the last ``lookback`` bars ending at ``index``.
        index: Bar to evaluate. Defaults to the latest candle.

    Returns:
        bool: True when a bullish harami is present at ``index`` (or in the lookback window).
    """
    index_ = absindex(index, len(candles))

    if lookback is None:
        return _bullish_harami(candles, index_)

    return any(
        _bullish_harami(candles, i) for i in utils.lookback_range(index_, lookback)
    )


def _bullish_harami(candles: list[Candle], index: int) -> bool:
    if index < 10:
        return False

    prev = candles[index - 1]
    curr = candles[index]

    if prev.realbody <= utils.candle_bodylong(candles, index - 1):
        return False
    if curr.realbody > utils.candle_bodyshort(candles, index):
        return False
    if not (
        curr.realbody_high < prev.realbody_high
        and curr.realbody_low > prev.realbody_low
    ):
        return False

    return prev.black_body


def bearish_harami(
    candles: list[Candle],
    lookback: int | None = None,
    index: int | None = None,
) -> bool:
    """Bearish Harami Pattern

    A bearish harami forms when a long bullish candle is followed by a short
    candle whose real body lies strictly inside the prior body.

    Source: https://github.com/TA-Lib/ta-lib

    Args:
        candles: Candle series to evaluate.
        lookback: When set, scan the last ``lookback`` bars ending at ``index``.
        index: Bar to evaluate. Defaults to the latest candle.

    Returns:
        bool: True when a bearish harami is present at ``index`` (or in the lookback window).
    """
    index_ = absindex(index, len(candles))

    if lookback is None:
        return _bearish_harami(candles, index_)

    return any(
        _bearish_harami(candles, i) for i in utils.lookback_range(index_, lookback)
    )


def _bearish_harami(candles: list[Candle], index: int) -> bool:
    if index < 10:
        return False

    prev = candles[index - 1]
    curr = candles[index]

    if prev.realbody <= utils.candle_bodylong(candles, index - 1):
        return False
    if curr.realbody > utils.candle_bodyshort(candles, index):
        return False
    if not (
        curr.realbody_high < prev.realbody_high
        and curr.realbody_low > prev.realbody_low
    ):
        return False

    return prev.white_body
