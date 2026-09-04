from ...core.candle import Candle
from ...utils.indexing import absindex
from .. import utils


def shooting_star(
    candles: list[Candle],
    lookback: int | None = None,
    index: int | None = None,
) -> bool:
    """Shooting Star Pattern

    A shooting star has a small real body, a long upper shadow, a very short lower
    shadow, and gaps up from the prior real body.

    Source: https://github.com/TA-Lib/ta-lib

    Args:
        candles: Candle series to evaluate.
        lookback: When set, scan the last ``lookback`` bars ending at ``index``.
        index: Bar to evaluate. Defaults to the latest candle.

    Returns:
        bool: True when a shooting star is present at ``index`` (or in the lookback window).
    """
    index_ = absindex(index, len(candles))

    if lookback is None:
        return _shooting_star(candles, index_)

    return any(
        _shooting_star(candles, i) for i in utils.lookback_range(index_, lookback)
    )


def _shooting_star(candles: list[Candle], index: int) -> bool:
    if index < 10:
        return False

    candle = candles[index]
    prev_candle = candles[index - 1]

    return (
        utils.realbody_gapup(candle, prev_candle)
        and candle.realbody < utils.candle_bodyshort(candles, index)
        and candle.shadow_upper > utils.candle_shadow_long(candles, index)
        and candle.shadow_lower < utils.candle_shadow_veryshort(candles, index)
    )
