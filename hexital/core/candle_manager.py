from __future__ import annotations

from copy import deepcopy
from datetime import timedelta
from typing import List, Optional, Set

from hexital.core.candle import Candle
from hexital.core.candlestick_type import CandlestickType
from hexital.exceptions import InvalidCandleOrder
from hexital.utils.candles import reading_by_candle
from hexital.utils.timeframe import (
    TimeFrame,
    clean_timestamp,
    on_timeframe,
    round_down_timestamp,
    timeframe_to_timedelta,
)

DEFAULT_CANDLES = "default"
_KEY_CONFIGS = ["candles_lifespan", "timeframe", "timeframe_fill"]


class CandleManager:
    candles: List[Candle]
    candles_lifespan: Optional[timedelta]
    timeframe: Optional[str] = None
    timeframe_fill: bool = False
    candlestick_type: Optional[CandlestickType] = None

    def __init__(
        self,
        candles: Optional[List[Candle]] = None,
        candles_lifespan: Optional[timedelta] = None,
        timeframe: Optional[str | TimeFrame] = None,
        timeframe_fill: bool = False,
        candlestick_type: Optional[CandlestickType] = None,
    ):
        if candles:
            self.candles = candles
        else:
            self.candles = []

        self.candles_lifespan = candles_lifespan

        if isinstance(timeframe, str):
            self.timeframe = timeframe.upper()
        elif isinstance(timeframe, TimeFrame):
            self.timeframe = timeframe.value
        self.timeframe_fill = timeframe_fill
        self.candlestick_type = candlestick_type

        self._tasks()

    def __eq__(self, other) -> bool:
        if not isinstance(other, CandleManager):
            return False
        for key in _KEY_CONFIGS:
            if getattr(self, key) != getattr(other, key):
                return False

        return True

    @property
    def name(self) -> str:
        return self.timeframe if self.timeframe else DEFAULT_CANDLES

    def _tasks(self):
        self.collapse_candles()
        self.convert_candles()
        self.trim_candles()

    def find_indicator(self, name: str) -> bool:
        for candle in reversed(self.candles):
            if reading_by_candle(candle, name):
                return True
        return False

    def append(self, candles: Candle | List[Candle] | dict | List[dict] | list | List[list]):
        candles_ = []

        if isinstance(candles, Candle):
            candles_.append(candles)
        elif isinstance(candles, dict):
            candles_.append(Candle.from_dict(candles))
        elif isinstance(candles, list):
            if not candles:
                pass
            elif isinstance(candles[0], Candle):
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

        self.candles.extend(deepcopy(candles_))
        self._tasks()

    def trim_candles(self):
        if self.candles_lifespan is None or not self.candles:
            return

        latest = self.candles[-1].timestamp
        if not latest:
            return

        while (
            self.candles[0].timestamp
            and self.candles[0].timestamp < latest - self.candles_lifespan
        ):
            self.candles.pop(0)

    def collapse_candles(self):
        """Collapses the given list of candles into specific timeframe candles.
        This can re-ran with same list to collapse latest candles.
        This method is destructive, returning a new list for the collapsed candles"""
        if not self.candles or not self.timeframe:
            return

        timeframe_ = timeframe_to_timedelta(self.timeframe)
        candles_ = [self.candles.pop(0)]
        init_candle = candles_[0]

        if init_candle.timestamp is None:
            return

        start_time = round_down_timestamp(init_candle.timestamp, timeframe_)
        end_time = start_time + timeframe_

        if not on_timeframe(init_candle.timestamp, timeframe_):
            init_candle.timestamp = end_time

        while self.candles:
            candle = self.candles.pop(0)
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

        if self.timeframe_fill:
            candles_ = self.fill_missing_candles(candles_, timeframe_)

        self.candles.extend(candles_)

    def fill_missing_candles(self, candles: List[Candle], timeframe: timedelta) -> List[Candle]:
        if len(candles) < 2:
            return candles

        index = 1

        while True:
            prev_candle = candles[index - 1]
            if (
                prev_candle.timestamp
                and candles[index].timestamp != prev_candle.timestamp + timeframe
            ):
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

    def convert_candles(self):
        if not self.candles or not self.candlestick_type:
            return

        self.candlestick_type.conversion(self.candles)

    def purge(self, indicator: str | Set[str]):
        """Remove this indicator value from all Candles"""
        if isinstance(indicator, str):
            for candle in self.candles:
                candle.indicators.pop(indicator, None)
                candle.sub_indicators.pop(indicator, None)
        else:
            for candle in self.candles:
                for name in indicator:
                    candle.indicators.pop(name, None)
                    candle.sub_indicators.pop(name, None)
