from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta
from functools import cmp_to_key
from typing import List, Optional, Set

from hexital.core.candle import Candle
from hexital.core.candlestick_type import CandlestickType
from hexital.exceptions import InvalidCandleOrder
from hexital.utils.candles import reading_by_candle
from hexital.utils.timeframe import (
    clean_timestamp,
    on_timeframe,
    round_down_timestamp,
    timedelta_to_str,
)

DEFAULT_CANDLES = "default"


class CandleManager:
    _name: Optional[str] = None
    candles: List[Candle]
    candle_life: Optional[timedelta]
    timeframe: Optional[timedelta] = None
    timeframe_fill: bool = False
    candlestick: Optional[CandlestickType] = None

    def __init__(
        self,
        candles: Optional[List[Candle]] = None,
        candle_life: Optional[timedelta] = None,
        timeframe: Optional[timedelta] = None,
        timeframe_fill: bool = False,
        candlestick: Optional[CandlestickType] = None,
    ):
        if candles:
            self.candles = candles
        else:
            self.candles = []

        self.candle_life = candle_life
        self.timeframe = timeframe
        self.timeframe_fill = timeframe_fill
        self.candlestick = candlestick

        self._tasks(True)

    def __eq__(self, other) -> bool:
        if not isinstance(other, CandleManager):
            return False

        for key in ["candle_life", "timeframe", "timeframe_fill"]:
            if getattr(self, key) != getattr(other, key):
                return False

        return True

    @property
    def name(self) -> str:
        if self._name:
            return self._name
        elif self.timeframe:
            return timedelta_to_str(self.timeframe)
        else:
            return DEFAULT_CANDLES

    @name.setter
    def name(self, name: str):
        self._name = name

    def _tasks(self, to_sort: Optional[bool] = False):
        if to_sort:
            self.sort_candles()

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
                return
            candle_ = candles[0]
            if isinstance(candle_, Candle):
                candles_.extend(candles)
            elif isinstance(candle_, dict):
                candles_.extend(Candle.from_dicts(candles))
            elif isinstance(candle_, (float, int, datetime)):
                candles_.append(Candle.from_list(candles))
            elif isinstance(candle_, list):
                candles_.extend(Candle.from_lists(candles))
            else:
                raise TypeError

        self.sort_candles(candles_)

        to_sort = False
        last_timestamp = self.candles[-1].timestamp if len(self.candles) > 0 else None

        for candle in candles_:
            if last_timestamp and candle.timestamp < last_timestamp:
                to_sort = True
            if not candle.timeframe or not self.timeframe:
                self.candles.append(deepcopy(candle))
            elif candle.timeframe <= self.timeframe:
                self.candles.append(deepcopy(candle))

        self._tasks(to_sort)

    def sort_candles(self, candles: Optional[List[Candle]] = None):
        """Sorts Candles in order of timestamp, accounts for collapsing"""
        if candles:
            candles.sort(key=cmp_to_key(self._sort_comparison))
        else:
            self.candles.sort(key=cmp_to_key(self._sort_comparison))

    def _sort_comparison(self, candle_one: Candle, candle_two: Candle) -> int:
        """Sort's Candles in order but if timeframe exists, sorts with collapsing in mind.
        So mixed order of candles will arrange for candles to be collapsed down based on given timeframe
        EG:
            No Timeframe : [09:05:00 09:02:00 09:10:00] > [09:02:00 09:05:00 09:10:00]
            T5 Timeframe : [09:05:00 09:02:00 09:10:00] > [09:05:00 09:02:00 09:10:00]
        """
        time_one = candle_one.timestamp.timestamp()
        time_two = candle_two.timestamp.timestamp()

        if not self.timeframe:
            return int(time_one - time_two)

        timeframe = self.timeframe.total_seconds()

        if (
            time_two % timeframe
            and not time_one % timeframe
            and candle_two.timestamp > candle_one.timestamp - self.timeframe
        ) or (
            time_one % timeframe
            and not time_two % timeframe
            and candle_one.timestamp > candle_two.timestamp - self.timeframe
        ):
            return 1

        return int(time_one - time_two)

    def trim_candles(self):
        if self.candle_life is None or not self.candles:
            return

        latest = self.candles[-1].timestamp

        while self.candles[0].timestamp and self.candles[0].timestamp < latest - self.candle_life:
            self.candles.pop(0)

    def collapse_candles(self):
        """Collapses the given list of candles into specific timeframe candles.
        This can re-ran with same list to collapse latest candles.
        This method is destructive, returning a new list for the collapsed candles"""
        if not self.candles or not self.timeframe:
            return

        candles_ = [self.candles.pop(0)]
        init_candle = candles_[0]
        init_candle.timeframe = self.timeframe

        start_time = round_down_timestamp(init_candle.timestamp, self.timeframe)
        end_time = start_time + self.timeframe

        if not on_timeframe(init_candle.timestamp, self.timeframe):
            init_candle.set_collapsed_timestamp(end_time)

        while self.candles:
            candle = self.candles.pop(0)
            prev_candle = candles_[-1]

            next_end_time = end_time + self.timeframe
            candle.timestamp = clean_timestamp(candle.timestamp)
            candle.timeframe = self.timeframe

            if start_time < candle.timestamp <= end_time and prev_candle.timestamp == end_time:
                prev_candle.merge(candle)
            elif (
                start_time - self.timeframe < candle.timestamp <= start_time
                and prev_candle.timestamp == start_time
            ):
                prev_candle.merge(candle)
            elif start_time < candle.timestamp <= end_time:
                candle.set_collapsed_timestamp(end_time)
                candles_.append(candle)
            elif end_time < candle.timestamp <= next_end_time:
                candle.set_collapsed_timestamp(next_end_time)
                candles_.append(candle)
                start_time = end_time
                end_time = next_end_time
            elif start_time < candle.timestamp and on_timeframe(candle.timestamp, self.timeframe):
                start_time = round_down_timestamp(candle.timestamp, self.timeframe)
                end_time = start_time + self.timeframe
                candle.set_collapsed_timestamp(start_time)
                candles_.append(candle)
            elif next_end_time < candle.timestamp:
                start_time = round_down_timestamp(candle.timestamp, self.timeframe)
                end_time = start_time + self.timeframe
                candle.set_collapsed_timestamp(end_time)
                candles_.append(candle)
            else:
                # Shit's fucked yo
                raise InvalidCandleOrder(
                    f"Failed to collapse_candles due to invalid candle order prev: [{prev_candle}] - current: [{candle}]",
                )

        if self.timeframe_fill:
            candles_ = self._fill_timeframe_candles(candles_, self.timeframe)

        self.candles.extend(candles_)

    @staticmethod
    def _fill_timeframe_candles(candles: List[Candle], timeframe: timedelta) -> List[Candle]:
        if len(candles) < 2:
            return candles

        index = 1

        while index < len(candles):
            prev_candle = candles[index - 1]
            if candles[index].timestamp != prev_candle.timestamp + timeframe:
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

        return candles

    def convert_candles(self):
        if self.candles and self.candlestick:
            self.candlestick.conversion(self.candles)

    def purge(self, indicator: str | Set[str]):
        """Remove this indicator value from all Candles"""
        if isinstance(indicator, str):
            indicator = indicator

        for candle in self.candles:
            for name in indicator:
                candle.indicators.pop(name, None)
                candle.sub_indicators.pop(name, None)
