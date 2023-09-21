from copy import deepcopy
from datetime import datetime, timedelta
from typing import List

from hexital.core.candle import Candle
from hexital.exceptions import InvalidTimeFrame

VALID_TIMEFRAME_PREFIXES = ["s", "t", "h", "d"]


def round_down_timestamp(timestamp: datetime, timeframe: timedelta) -> datetime:
    rounded_datetime_seconds = (
        timestamp.timestamp() // timeframe.total_seconds() * timeframe.total_seconds()
    )

    return datetime.fromtimestamp(rounded_datetime_seconds)


def timeframe_to_timedelta(timeframe: str) -> timedelta:
    # https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases
    if not isinstance(timeframe[0], str) or timeframe[0] not in VALID_TIMEFRAME_PREFIXES:
        raise InvalidTimeFrame(
            f"Invalid value: {timeframe}, valid are: {VALID_TIMEFRAME_PREFIXES}"
        )
    if timeframe.startswith("s"):
        return timedelta(seconds=int(timeframe[1:]))
    if timeframe.startswith("t"):
        return timedelta(minutes=int(timeframe[1:]))
    if timeframe.startswith("h"):
        return timedelta(hours=int(timeframe[1:]))
    if timeframe.startswith("d"):
        return timedelta(days=int(timeframe[1:]))

    return timedelta(seconds=0)


def merge_candles(candles: List[Candle], timeframe: str):
    if not candles:
        return []

    candles_ = deepcopy(candles)
    timeframe_delta = timeframe_to_timedelta(timeframe)

    collapsed_candles = [candles_.pop(0)]

    if collapsed_candles[0].timestamp.timestamp() % timeframe_delta.total_seconds() == 0:
        if len(candles) > 0:
            collapsed_candles.append(candles_.pop(0))

    if not candles:
        return collapsed_candles

    start_timestamp = round_down_timestamp(
        collapsed_candles[0].timestamp, timeframe_delta
    )
    collapsed_candles[-1].timestamp = start_timestamp + timeframe_delta

    while candles_:
        candle = candles_.pop(0)
        end_timestamp = start_timestamp + timeframe_delta

        if start_timestamp < candle.timestamp <= end_timestamp:
            collapsed_candles[-1].merge(candle)
        else:
            start_timestamp = round_down_timestamp(candle.timestamp, timeframe_delta)
            candle.timestamp = start_timestamp + timeframe_delta
            collapsed_candles.append(candle)

    return collapsed_candles
