from ...core.candle import Candle
from ...utils.indexing import absindex
from .. import utils


def spinning_top(
    candles: list[Candle],
    lookback: int | None = None,
    index: int | None = None,
) -> bool:
    """Spinning Top Pattern

    A spinning top has a small real body with upper and lower shadows longer than
    the body.

    Source: https://github.com/TA-Lib/ta-lib

    Args:
        candles: Candle series to evaluate.
        lookback: When set, scan the last ``lookback`` bars ending at ``index``.
        index: Bar to evaluate. Defaults to the latest candle.

    Returns:
        bool: True when a spinning top is present at ``index`` (or in the lookback window).
    """
    index_ = absindex(index, len(candles))

    if lookback is None:
        return _spinning_top(candles, index_)

    return any(
        _spinning_top(candles, i) for i in utils.lookback_range(index_, lookback)
    )


def _spinning_top(candles: list[Candle], index: int) -> bool:
    if index < 10:
        return False

    candle = candles[index]

    return (
        candle.realbody < utils.candle_bodyshort(candles, index)
        and candle.shadow_upper > candle.realbody
        and candle.shadow_lower > candle.realbody
    )
