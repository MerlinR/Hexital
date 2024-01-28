from typing import List, Optional

from hexital.core.candle import Candle


def realbody_avg(candles: List[Candle], length: int, index: Optional[int] = None) -> float:
    if index is None:
        index = len(candles) - 1

    return (
        sum(
            candles[i].realbody()
            for i in range(0 if index - length < 0 else index - length, index)
        )
        / length
    )


def shadow_upper_avg(candles: List[Candle], length: int, index: Optional[int] = None) -> float:
    if index is None:
        index = len(candles) - 1

    return (
        sum(
            candles[i].shadow_upper()
            for i in range(0 if index - length < 0 else index - length, index)
        )
        / length
    )


def shadow_lower_avg(candles: List[Candle], length: int, index: Optional[int] = None) -> float:
    if index is None:
        index = len(candles) - 1

    return (
        sum(
            candles[i].shadow_lower()
            for i in range(0 if index - length < 0 else index - length, index)
        )
        / length
    )


def high_low_avg(candles: List[Candle], length: int, index: Optional[int] = None) -> float:
    if index is None:
        index = len(candles) - 1

    return (
        sum(
            candles[i].high_low()
            for i in range(0 if index - length < 0 else index - length, index)
        )
        / length
    )
