from itertools import chain
from typing import List, Optional

from hexital.core.candle import Candle
from hexital.lib.timeframe_utils import round_down_timestamp, timeframe_to_timedelta


def reading_by_index(
    candles: List[Candle], name: str, index: int = -1
) -> float | dict | None:
    """Simple method to get a reading from the given indicator from it's index"""
    if index is None:
        index = -1
    return reading_by_candle(candles[index], name)


def reading_by_candle(candle: Candle, name: str) -> float | dict | None:
    """Simple method to get a reading from the given indicator from a candle
    Uses '.' to find nested reading, E.G 'MACD_12_26_9.MACD"""

    if "." in name:
        main_name, nested_name = name.split(".")
        reading = _nested_indicator(candle, main_name, nested_name)
        if reading:
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
        if isinstance(candle.indicators[name], dict):
            return candle.indicators[name].get(nested_name)
        return candle.indicators[name]

    if name in candle.sub_indicators:
        if isinstance(candle.sub_indicators[name], dict):
            return candle.sub_indicators[name].get(nested_name)
        return candle.sub_indicators[name]

    for key, reading in chain(candle.indicators.items(), candle.sub_indicators.items()):
        if name in key:
            if isinstance(reading, dict):
                return reading.get(nested_name)
            return reading
    return None


def reading_count(candles: List[Candle], name: str) -> int:
    """Returns how many instance of the given indicator exist"""
    count = 0
    for candle in reversed(candles):
        if not reading_by_candle(candle, name):
            return count
        count += 1

    return count


def reading_as_list(candles: List[Candle], name: str) -> List[float | dict]:
    """Gathers the indicator for all candles as a list"""
    return [candle.indicators.get(name) for candle in candles]


def reading_period(
    candles: List[Candle], period: int, name: str, index: Optional[int] = None
) -> bool:
    """Will return True if the given indicator goes back as far as amount,
    It's true if exactly or more than. Period will be period-1"""
    if index is None:
        index = len(candles) - 1

    period -= 1

    if (index - period) < 0:
        return False

    # Checks 3 points along period to verify values exist
    return all(
        True
        if reading_by_index(
            candles,
            name,
            index - int(point),
        )
        is not None
        else False
        for point in [
            period,
            period / 2,
            0,
        ]
    )


def collapse_candles_timeframe(candles: List[Candle], timeframe: str, fill: bool = False):
    if not candles:
        return []

    timeframe_delta = timeframe_to_timedelta(timeframe)

    collapsed_candles = [candles.pop(0)]

    start_timestamp = round_down_timestamp(
        collapsed_candles[0].timestamp, timeframe_delta
    )

    if collapsed_candles[0].timestamp.timestamp() % timeframe_delta.total_seconds() != 0:
        collapsed_candles[0].timestamp = start_timestamp + timeframe_delta

    while candles:
        candle = candles.pop(0)

        # If current candle before the lastest collapsed candle
        if start_timestamp + timeframe_delta > candle.timestamp:
            start_timestamp = round_down_timestamp(candle.timestamp, timeframe_delta)

        end_timestamp = start_timestamp + timeframe_delta

        # If candle time is within current candle timeframe
        if start_timestamp < candle.timestamp <= end_timestamp:
            # If prev candle the end of current timeframe
            if collapsed_candles[-1].timestamp == end_timestamp:
                collapsed_candles[-1].merge(candle)
            else:
                candle.timestamp = end_timestamp
                collapsed_candles.append(candle)
                start_timestamp = round_down_timestamp(candle.timestamp, timeframe_delta)
        # If candle is outside current candle timeframe
        else:
            start_timestamp = round_down_timestamp(candle.timestamp, timeframe_delta)
            end_timestamp = start_timestamp + timeframe_delta
            candle.timestamp = end_timestamp
            collapsed_candles.append(candle)

    if fill:
        index = 1
        while True:
            prev_candle = collapsed_candles[index - 1]
            if (
                collapsed_candles[index].timestamp
                != prev_candle.timestamp + timeframe_delta
            ):
                fill_candle = Candle(
                    open=prev_candle.open,
                    close=prev_candle.close,
                    high=prev_candle.high,
                    low=prev_candle.low,
                    volume=prev_candle.volume,
                    timestamp=prev_candle.timestamp + timeframe_delta,
                )
                collapsed_candles.insert(index, fill_candle)

            index += 1
            if index >= len(collapsed_candles):
                break

    return collapsed_candles
