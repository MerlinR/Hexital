from typing import List, Optional

from hexital.analysis.movement import positive
from hexital.core.candle import Candle


def candle_realbody(candle: Candle) -> float:
    return abs(candle.open - candle.close)


def candle_shadow_upper(candle: Candle) -> float:
    if positive(candle):
        return abs(candle.high - candle.close)
    return abs(candle.high - candle.open)


def candle_shadow_lower(candle: Candle) -> float:
    if positive(candle):
        return abs(candle.low - candle.open)
    return abs(candle.low - candle.close)


def candle_high_low(candle: Candle) -> float:
    return abs(candle.high - candle.low)


def candle_realbody_avg(candles: List[Candle], length: int, index: Optional[int] = None) -> float:
    if index is None:
        index = len(candles) - 1

    return (
        sum(
            candle_realbody(candles[i])
            for i in range(0 if index - length < 0 else index - length, index)
        )
        / length
    )


def candle_shadow_upper_avg(
    candles: List[Candle], length: int, index: Optional[int] = None
) -> float:
    if index is None:
        index = len(candles) - 1

    return (
        sum(
            candle_shadow_upper(candles[i])
            for i in range(0 if index - length < 0 else index - length, index)
        )
        / length
    )


def candle_shadow_lower_avg(
    candles: List[Candle], length: int, index: Optional[int] = None
) -> float:
    if index is None:
        index = len(candles) - 1

    return (
        sum(
            candle_shadow_lower(candles[i])
            for i in range(0 if index - length < 0 else index - length, index)
        )
        / length
    )


def candle_high_low_avg(candles: List[Candle], length: int, index: Optional[int] = None) -> float:
    if index is None:
        index = len(candles) - 1

    return (
        sum(
            candle_high_low(candles[i])
            for i in range(0 if index - length < 0 else index - length, index)
        )
        / length
    )
