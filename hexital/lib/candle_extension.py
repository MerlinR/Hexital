from datetime import timedelta
from itertools import chain
from typing import List, Optional
from hexital.exceptions import InvalidCandleOrder
from hexital.core.candle import Candle
from hexital.lib.timeframe_utils import (
    round_down_timestamp,
    timeframe_to_timedelta,
    clean_timestamp,
    on_timeframe,
    TimeFrame,
)
from hexital.lib.utils import absindex, valid_index


def reading_by_index(candles: List[Candle], name: str, index: int = -1) -> float | dict | None:
    """Simple method to get a reading from the given indicator from it's index"""
    if not valid_index(index, len(candles)):
        return None

    return reading_by_candle(candles[index], name)


def reading_by_candle(candle: Candle, name: str) -> float | dict | None:
    """Simple method to get a reading from the given indicator from a candle
    Uses '.' to find nested reading, E.G 'MACD_12_26_9.MACD"""

    if "." in name:
        main_name, nested_name = name.split(".")
        reading = _nested_indicator(candle, main_name, nested_name)
        if reading is not None:
            return reading

    if getattr(candle, name, None) is not None:
        return getattr(candle, name)

    if name in candle.indicators:
        return candle.indicators[name]

    if name in candle.sub_indicators:
        return candle.sub_indicators[name]

    for key, reading in chain(candle.indicators.items(), candle.sub_indicators.items()):
        if name in key:
            return reading

    return None


def _nested_indicator(candle: Candle, name: str, nested_name: str) -> float | None:
    if name in candle.indicators:
        val_ = candle.indicators[name]
        return val_.get(nested_name) if isinstance(val_, dict) else val_

    if name in candle.sub_indicators:
        val_ = candle.sub_indicators[name]
        return val_.get(nested_name) if isinstance(val_, dict) else val_

    for key, reading in chain(candle.indicators.items(), candle.sub_indicators.items()):
        if name in key:
            return reading.get(nested_name) if isinstance(reading, dict) else reading

    return None


def reading_count(candles: List[Candle], name: str) -> int:
    """Returns how many instance of the given indicator exist"""
    for count, candle in enumerate(reversed(candles)):
        if not reading_by_candle(candle, name):
            return count

    return len(candles)


def reading_as_list(candles: List[Candle], name: str) -> List[float | dict | None]:
    """Gathers the indicator for all candles as a list"""
    return [candle.indicators.get(name) for candle in candles]


def reading_period(
    candles: List[Candle], period: int, name: str, index: Optional[int] = None
) -> bool:
    """Will return True if the given indicator goes back as far as amount,
    It's true if exactly or more than. Period will be period-1"""
    period -= 1

    if index is None:
        index = len(candles) - 1

    if (index - period) < 0:
        return False

    # Checks 3 points along period to verify values exist
    return all(
        bool(
            reading_by_index(
                candles,
                name,
                index - int(point),
            )
            is not None
        )
        for point in [
            period,
            period / 2,
            0,
        ]
    )


def candles_sum(
    candles: List[Candle], indicator: str, length: int, index: int = -1
) -> float | None:
    """Sum of `indicator` for `length` bars back. including index/latest"""
    index_ = absindex(index, len(candles))
    if not index_:
        return

    index_ += 1

    length = len(candles) if length > len(candles) else length
    values = [reading_by_candle(candle, indicator) for candle in candles[index_ - length : index_]]

    return sum(value for value in values if value and isinstance(value, (int, float)))


def collapse_candles_timeframe(
    candles: List[Candle], timeframe: str | TimeFrame, fill_missing: bool = False
) -> List[Candle]:
    """Collapses the given list of candles into specific timeframe candles.
    This can re-ran with same list to collapse latest candles.
    This method is destructive, returning a new list for the collapsed candles"""
    if not candles:
        return []

    timeframe_ = timeframe_to_timedelta(timeframe)
    candles_ = [candles.pop(0)]
    init_candle = candles_[0]

    if init_candle.timestamp is None:
        return candles

    start_time = round_down_timestamp(init_candle.timestamp, timeframe_)
    end_time = start_time + timeframe_

    if not on_timeframe(init_candle.timestamp, timeframe_):
        init_candle.timestamp = end_time

    while candles:
        candle = candles.pop(0)
        prev_candle = candles_[-1]

        if not candle.timestamp or not prev_candle.timestamp:
            continue

        candle.timestamp = clean_timestamp(candle.timestamp)

        next_candle = end_time + timeframe_

        if start_time < candle.timestamp <= end_time and prev_candle.timestamp == end_time:
            prev_candle.merge(candle)
        elif start_time < candle.timestamp <= end_time:
            candle.timestamp = end_time
            candles_.append(candle)
        elif (
            start_time - timeframe_ < candle.timestamp <= start_time
            and prev_candle.timestamp == start_time
        ):
            prev_candle.merge(candle)
        elif end_time < candle.timestamp <= next_candle:
            candle.timestamp = next_candle
            candles_.append(candle)
            start_time += timeframe_
            end_time += timeframe_
        elif start_time < candle.timestamp and on_timeframe(candle.timestamp, timeframe_):
            start_time = round_down_timestamp(candle.timestamp, timeframe_)
            end_time = start_time + timeframe_
            candle.timestamp = start_time
            candles_.append(candle)
        elif next_candle < candle.timestamp:
            start_time = round_down_timestamp(candle.timestamp, timeframe_)
            end_time = start_time + timeframe_
            candle.timestamp = end_time
            candles_.append(candle)
        else:
            # Shit's fucked yo
            raise InvalidCandleOrder(
                f"Failed to collapse_candles due to invalid candle order prev: [{prev_candle}] - current: [{candle}]",
            )

    if fill_missing:
        candles_ = fill_missing_candles(candles_, timeframe_)

    return candles_


def fill_missing_candles(candles: List[Candle], timeframe: timedelta) -> List[Candle]:
    if len(candles) < 2:
        return candles

    index = 1

    while True:
        prev_candle = candles[index - 1]
        if prev_candle.timestamp and candles[index].timestamp != prev_candle.timestamp + timeframe:
            fill_candle = Candle(
                open=prev_candle.close,
                close=prev_candle.close,
                high=prev_candle.close,
                low=prev_candle.close,
                volume=0,
                timestamp=prev_candle.timestamp + timeframe,
            )
            candles.insert(index, fill_candle)

        index += 1
        if index >= len(candles):
            break
    return candles


def trim_candles(candles: List[Candle], lifespan: Optional[timedelta] = None):
    if lifespan is None or not candles:
        return

    latest = candles[-1].timestamp
    if not latest:
        return

    while candles[0].timestamp and candles[0].timestamp < latest - lifespan:
        candles.pop(0)


def multi_convert_candles(
    candles: Candle | List[Candle] | dict | List[dict] | list | List[list],
) -> List[Candle]:
    candles_ = []

    if isinstance(candles, Candle):
        candles_.append(candles)
    elif isinstance(candles, dict):
        candles_.append(Candle.from_dict(candles))
    elif isinstance(candles, list):
        if isinstance(candles[0], Candle):
            candles_.extend(candles)
        elif isinstance(candles[0], dict):
            candles_.extend(Candle.from_dicts(candles))
        elif isinstance(candles[0], (float, int)):
            candles_.append(Candle.from_list(candles))
        elif isinstance(candles[0], list):
            candles_.extend(Candle.from_lists(candles))
        else:
            raise TypeError
    else:
        raise TypeError

    return candles_
