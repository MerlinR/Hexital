from ...core.candle import Candle
from ...utils.indexing import absindex
from .. import utils


def bullish_engulfing(
    candles: list[Candle],
    lookback: int | None = None,
    index: int | None = None,
) -> bool:
    """Bullish Engulfing Pattern

    A bullish engulfing forms when a bearish candle is followed by a larger bullish
    candle whose real body fully covers the prior real body.

    Source: https://github.com/TA-Lib/ta-lib

    Args:
        candles: Candle series to evaluate.
        lookback: When set, scan the last ``lookback`` bars ending at ``index``.
        index: Bar to evaluate. Defaults to the latest candle.

    Returns:
        bool: True when a bullish engulfing is present at ``index`` (or in the lookback window).
    """
    index_ = absindex(index, len(candles))

    if lookback is None:
        return _bullish_engulfing(candles, index_)

    return any(
        _bullish_engulfing(candles, i) for i in utils.lookback_range(index_, lookback)
    )


def _bullish_engulfing(candles: list[Candle], index: int) -> bool:
    if index < 1:
        return False

    prev = candles[index - 1]
    curr = candles[index]

    if not curr.white_body or not prev.black_body:
        return False

    engulfs = (curr.close >= prev.open and curr.open < prev.close) or (
        curr.close > prev.open and curr.open <= prev.close
    )
    if not engulfs:
        return False

    # TA-Lib returns +/-100 only when bodies do not match on either end.
    return curr.open != prev.close and curr.close != prev.open


def bearish_engulfing(
    candles: list[Candle],
    lookback: int | None = None,
    index: int | None = None,
) -> bool:
    """Bearish Engulfing Pattern

    A bearish engulfing forms when a bullish candle is followed by a larger bearish
    candle whose real body fully covers the prior real body.

    Source: https://github.com/TA-Lib/ta-lib

    Args:
        candles: Candle series to evaluate.
        lookback: When set, scan the last ``lookback`` bars ending at ``index``.
        index: Bar to evaluate. Defaults to the latest candle.

    Returns:
        bool: True when a bearish engulfing is present at ``index`` (or in the lookback window).
    """
    index_ = absindex(index, len(candles))

    if lookback is None:
        return _bearish_engulfing(candles, index_)

    return any(
        _bearish_engulfing(candles, i) for i in utils.lookback_range(index_, lookback)
    )


def _bearish_engulfing(candles: list[Candle], index: int) -> bool:
    if index < 1:
        return False

    prev = candles[index - 1]
    curr = candles[index]

    if not curr.black_body or not prev.white_body:
        return False

    engulfs = (curr.open >= prev.close and curr.close < prev.open) or (
        curr.open > prev.close and curr.close <= prev.open
    )
    if not engulfs:
        return False

    return curr.open != prev.close and curr.close != prev.open
