from __future__ import annotations

from datetime import datetime, timedelta
from functools import cmp_to_key
from typing import List, Optional, Set, TypeAlias

from hexital.core.candle import Candle
from hexital.core.candlestick_type import CandlestickType
from hexital.exceptions import InvalidCandleOrder
from hexital.utils.candles import reading_by_candle
from hexital.utils.common import CalcMode
from hexital.utils.timeframe import (
    on_timeframe,
    round_down_timestamp,
    timedelta_to_str,
    trim_timestamp,
)

Candles: TypeAlias = Candle | List[Candle] | dict | List[dict] | list | List[list]

DEFAULT_CANDLES = "default"


class CandleManager:
    _name: Optional[str] = None
    _candles: List[Candle]
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
        self.candle_life = candle_life
        self.timeframe = timeframe
        self.timeframe_fill = timeframe_fill
        self._candles = candles if candles else []

        if candlestick:
            self.candlestick = candlestick
            self.candlestick.set_candle_refs(self._candles)

        if self._candles:
            self._candle_tasks()

    def __eq__(self, other) -> bool:
        if not isinstance(other, CandleManager):
            return False

        for key in ["candle_life", "timeframe", "timeframe_fill", "candlestick"]:
            if getattr(self, key) != getattr(other, key):
                return False

        return True

    @property
    def name(self) -> str:
        if self._name:
            return self._name
        elif self.candlestick and self.timeframe:
            return f"{timedelta_to_str(self.timeframe)}_{self.candlestick.acronym}"
        elif self.timeframe:
            return timedelta_to_str(self.timeframe)
        elif self.candlestick:
            return self.candlestick.acronym
        else:
            return DEFAULT_CANDLES

    @name.setter
    def name(self, name: str):
        self._name = name

    @property
    def candles(self) -> List[Candle]:
        if self.candlestick:
            return self.candlestick.derived_candles
        return self._candles

    @candles.setter
    def candles(self, candles: List[Candle]):
        """Set the Candles in Candlestick manager and reset transformed Candles"""
        self._candles = candles
        if self.candlestick:
            self.candlestick.derived_candles.reset()

    def _candle_tasks(
        self,
        mode: CalcMode = CalcMode.INSERT,
        index: Optional[int] = None,
    ):
        self.resample_candles(mode, index)
        self.candlestick_conversion(mode, index)
        self.trim_candles()

    def find_indicator(self, name: str) -> bool:
        for candle in reversed(self.candles):
            if reading_by_candle(candle, name):
                return True
        return False

    def _parse_candles(self, candles: Candles) -> List[Candle]:
        candles_ = []

        if isinstance(candles, Candle):
            candles_.append(candles)
        elif isinstance(candles, dict):
            candles_.append(Candle.from_dict(candles))
        elif isinstance(candles, list) and candles:
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

        return candles_

    def prepend(self, candles: Candles):
        candles_ = self._parse_candles(candles)

        for candle in reversed(candles_):
            if self.timeframe and candle.timeframe and candle.timeframe > self.timeframe:
                continue
            self._candles.insert(0, candle.clean_copy())

        self._candle_tasks(CalcMode.PREPEND)

    def append(self, candles: Candles):
        candles_ = self._parse_candles(candles)
        index = len(self._candles) - 1 if len(self._candles) > 0 else 0

        for candle in candles_:
            if self.timeframe and candle.timeframe and candle.timeframe > self.timeframe:
                continue

            self._candles.append(candle.clean_copy())

        self._candle_tasks(CalcMode.APPEND, index)

    def insert(self, candles: Candles):
        candles_ = self._parse_candles(candles)

        self.sort_candles(candles_)

        to_sort = False
        last_timestamp = self._candles[-1].timestamp if self._candles else None

        for candle in candles_:
            if self.timeframe and candle.timeframe and candle.timeframe > self.timeframe:
                continue
            elif last_timestamp and candle.timestamp < last_timestamp:
                to_sort = True

            self._candles.append(candle.clean_copy())

        if to_sort:
            self.sort_candles()

        self._candle_tasks(CalcMode.INSERT)

    def sort_candles(self, candles: Optional[List[Candle]] = None):
        """Sorts Candles in order of timestamp, accounts for collapsing"""
        if candles:
            candles.sort(key=cmp_to_key(self._sort_comparison))
        else:
            self._candles.sort(key=cmp_to_key(self._sort_comparison))

    def _sort_comparison(self, candle_one: Candle, candle_two: Candle) -> int:
        """Sort's Candles in order but if timeframe exists, sorts with collapsing in mind.
        So mixed order of candles will arrange for candles to be resampled down based on given timeframe
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
        if self.candle_life is None or not self._candles:
            return

        while (
            self._candles[0].timestamp
            and self._candles[-1].timestamp
            and self._candles[0].timestamp < self._candles[-1].timestamp - self.candle_life
        ):
            self._candles.pop(0)

    def resample_candles(
        self,
        mode: CalcMode,
        index: Optional[int] = None,
    ):
        """resamples the given list of candles into specific timeframe candles.
        This can re-ran with same list to resample latest candles.
        This method is destructive, generating a new list for the resampled candles"""
        if mode == CalcMode.INSERT:
            start_index = 0
        elif index is not None:
            start_index = index
        else:
            start_index = self._find_resample_index()

        if len(self._candles) <= start_index + 1 or not self.timeframe:
            return

        end_index = len(self._candles)

        candles_ = [self._candles.pop(start_index)]

        init_candle = candles_[0]
        init_candle.timeframe = self.timeframe
        if not init_candle.timestamp:
            return

        start_time = round_down_timestamp(init_candle.timestamp, self.timeframe)
        end_time = start_time + self.timeframe

        if not on_timeframe(init_candle.timestamp, self.timeframe):
            init_candle.set_resampled_timestamp(end_time)

        for _ in range(abs(end_index - start_index)):
            if len(self._candles) <= start_index:
                break

            candle = self._candles.pop(start_index)
            prev_candle = candles_[-1]

            if not candle.timestamp:
                return

            if (
                mode != CalcMode.INSERT
                and candle.timeframe == self.timeframe
                and prev_candle.timeframe == self.timeframe
            ):
                candles_.append(candle)
                break

            next_end_time = end_time + self.timeframe
            candle.timestamp = trim_timestamp(candle.timestamp)
            candle.timeframe = self.timeframe

            if start_time < candle.timestamp <= end_time and prev_candle.timestamp == end_time:
                prev_candle.merge(candle)
            elif (
                start_time - self.timeframe < candle.timestamp <= start_time
                and prev_candle.timestamp == start_time
            ):
                prev_candle.merge(candle)
            elif start_time < candle.timestamp <= end_time:
                candle.set_resampled_timestamp(end_time)
                candles_.append(candle)
            elif end_time < candle.timestamp <= next_end_time:
                candle.set_resampled_timestamp(next_end_time)
                candles_.append(candle)
                start_time = end_time
                end_time = next_end_time
            elif start_time < candle.timestamp and on_timeframe(candle.timestamp, self.timeframe):
                start_time = round_down_timestamp(candle.timestamp, self.timeframe)
                end_time = start_time + self.timeframe
                candle.set_resampled_timestamp(start_time)
                candles_.append(candle)
            elif next_end_time < candle.timestamp:
                start_time = round_down_timestamp(candle.timestamp, self.timeframe)
                end_time = start_time + self.timeframe
                candle.set_resampled_timestamp(end_time)
                candles_.append(candle)
            else:
                # Shit's fucked yo
                raise InvalidCandleOrder(
                    f"Failed to resample_candles due to invalid candle order prev: [{prev_candle}] - current: [{candle}]",
                )

        if self.timeframe_fill:
            candles_ = self._fill_timeframe_candles(
                candles_, self.timeframe, start_index, end_index
            )

        self._candles[start_index:start_index] = candles_

    def _find_resample_index(self) -> int:
        """Optimisation method, to find where to start calculating the indicator from
        Searches from newest to oldest to find the first candle without the indicator
        """
        if (
            not self.candles
            or not self.candles[0].timeframe
            or self.candles[0].timeframe != self.timeframe
        ):
            return 0

        for index in range(len(self.candles) - 1, -1, -1):
            if self.candles[index].timeframe == self.timeframe:
                return index + 1
        return 0

    @staticmethod
    def _fill_timeframe_candles(
        candles: List[Candle],
        timeframe: timedelta,
        start_index: int = 0,
        end_index: Optional[int] = None,
    ) -> List[Candle]:
        """Generates filler Candle's to the list of Candles.
        Filler Candles are Candles that fill gaps of timeframed Candles,
        which are simply filled with previous Candle's 'close' value."""
        if len(candles) < 2:
            return candles

        index = start_index if start_index != 0 else 1

        end_index_ = end_index if end_index else len(candles)

        while index < end_index_ + 1:
            if len(candles) <= index:
                break

            prev_candle = candles[index - 1]

            if prev_candle.timestamp is None:
                # TODO Add logger warning?
                break

            if candles[index].timestamp != prev_candle.timestamp + timeframe:
                fill_candle = Candle(
                    open=prev_candle.close,
                    close=prev_candle.close,
                    high=prev_candle.close,
                    low=prev_candle.close,
                    volume=0,
                    timestamp=prev_candle.timestamp + timeframe,
                    timeframe=prev_candle.timeframe,
                )
                fill_candle.aggregation_factor = 0
                candles.insert(index, fill_candle)
                end_index_ += 1

            index += 1

        return candles

    def candlestick_conversion(self, mode: CalcMode, index: Optional[int] = None):
        if self.candlestick:
            self.candlestick.transform(mode, index)

    def purge(self, indicator: str | Set[str]):
        """Remove this indicator value from all Candles"""
        if isinstance(indicator, str):
            indicator = {indicator}

        for candle in self.candles:
            for name in indicator:
                candle.indicators.pop(name, None)
                candle.sub_indicators.pop(name, None)
