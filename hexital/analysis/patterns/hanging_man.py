from ...core.candle import Candle
from ...utils.indexing import absindex
from .. import utils


def hanging_man(
    candles: list[Candle],
    lookback: int | None = None,
    index: int | None = None,
) -> bool:
    """Hanging Man Pattern

    A hanging man has a small real body, a long lower shadow, a very short upper
    shadow, and sits near the highs of the prior candle.

    Source: https://github.com/TA-Lib/ta-lib

    Args:
        candles: Candle series to evaluate.
        lookback: When set, scan the last ``lookback`` bars ending at ``index``.
        index: Bar to evaluate. Defaults to the latest candle.

    Returns:
        bool: True when a hanging man is present at ``index`` (or in the lookback window).
    """
    index_ = absindex(index, len(candles))

    if lookback is None:
        return _hanging_man(candles, index_)

    return any(
        _hanging_man(candles, i) for i in utils.lookback_range(index_, lookback)
    )


def _hanging_man(candles: list[Candle], index: int) -> bool:
    if index < 10:
        return False

    candle = candles[index]
    prev_candle = candles[index - 1]

    return (
        candle.realbody < utils.candle_bodyshort(candles, index)
        and candle.shadow_lower > utils.candle_shadow_long(candles, index)
        and candle.shadow_upper < utils.candle_shadow_veryshort(candles, index)
        and candle.realbody_low
        >= prev_candle.high - utils.candle_near(candles, index - 1)
    )
