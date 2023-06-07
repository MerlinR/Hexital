from itertools import chain
from typing import Dict, List

from hexital.types.ohlcv import OHLCV


def indicator_by_index(
    candles: List[OHLCV], name: str, index: int = None
) -> float | dict | None:
    """Simple method to get an indicator value from it's index,
    regardless of it's location"""
    if index is None:
        index = len(candles) - 1

    return indicator_by_candle(candles[index], name)


def indicator_by_candle(candle: OHLCV, name: str) -> float | dict | None:
    """Simple method to get an indicator value from a candle,
    regardless of it's location"""

    if "." in name:
        main_name, nested_name = name.split(".")
        value = _nested_indicator(candle, main_name, nested_name)
        if value:
            return value

    if getattr(candle, name, None) is not None:
        return getattr(candle, name)

    if name in candle.indicators:
        return candle.indicators[name]

    if name in candle.sub_indicators:
        return candle.sub_indicators[name]

    for key, value in chain(candle.indicators.items(), candle.sub_indicators.items()):
        if name in key:
            return value

    return None


def _nested_indicator(candle: OHLCV, name: str, nested_name: str) -> float | None:
    if name in candle.indicators:
        if isinstance(candle.indicators[name], dict):
            return candle.indicators[name].get(nested_name)
        return candle.indicators[name]

    if name in candle.sub_indicators:
        if isinstance(candle.sub_indicators[name], dict):
            return candle.sub_indicators[name].get(nested_name)
        return candle.sub_indicators[name]

    for key, value in chain(candle.indicators.items(), candle.sub_indicators.items()):
        if name in key:
            if isinstance(value, dict):
                return value.get(nested_name)
            return value
    return None


def indicator_count(candles: List[OHLCV], name: str) -> int:
    """Returns how many instance of the given indicator exist"""
    count = 0
    for candle in candles:
        if indicator_by_candle(candle, name):
            count += 1

    return count


def indicator_as_list(candles: List[OHLCV], name: str) -> List[float | dict]:
    """Gathers the indicator for all candles as a list"""
    return [candle.indicators.get(name) for candle in candles]


def indicator_period(
    candles: List[OHLCV], period: int, name: str, index: int = None
) -> bool:
    """Will return True if the given indicator goes back as far as amount,
    It's true if exactly or more than. Period will be period -1"""
    if index is None:
        index = len(candles) - 1

    period -= 1

    if (index - period) < 0:
        return False

    # Checks 3 points along period to verify values exist
    return all(
        indicator_by_index(
            candles,
            name,
            index - int(x),
        )
        for x in [
            period,
            period / 2,
            0,
        ]
    )


def round_values(
    values: float | Dict[str, float], round_by: int = 4
) -> float | Dict[str, float]:
    if isinstance(values, dict):
        for key, val in values.items():
            if isinstance(val, float):
                values[key] = round(val, round_by)
    elif isinstance(values, float):
        values = round(values, round_by)

    return values
