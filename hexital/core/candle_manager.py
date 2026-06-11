from __future__ import annotations

from datetime import timedelta
from functools import cmp_to_key

from ..exceptions import InvalidCandleOrder
from ..utils.candles import Candles, parse_candles, reading_by_candle
from ..utils.common import CalcMode
from ..utils.timeframe import (
    NullTimeFrame,
    on_timeframe,
    round_down_timestamp,
    timedelta_to_str,
)
from .candle import Candle
from .candlestick_type import CandlestickType


class CandleManager:
    _name: str | None = None
    _candles: list[Candle]
    candle_life: timedelta | None
    timeframe: timedelta | None = None
    timeframe_fill: bool = False
    candlestick: CandlestickType | None = None

    def __init__(
        self,
        candles: list[Candle] | None = None,
        candle_life: timedelta | None = None,
        timeframe: timedelta | None = None,
        timeframe_fill: bool = False,
        candlestick: CandlestickType | None = None,
    ):
        self.candle_life = candle_life
        self.timeframe = timeframe
        self.timeframe_fill = timeframe_fill
        self._candles = []
        if candles:
            self._candles.extend(candles)

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
        if self.candlestick and self.timeframe:
            return f"{timedelta_to_str(self.timeframe)}_{self.candlestick.acronym}"
        if self.timeframe:
            return timedelta_to_str(self.timeframe)
        if self.candlestick:
            return self.candlestick.acronym
        return NullTimeFrame.name

    @name.setter
    def name(self, name: str):
        self._name = name

    @property
    def candles(self) -> list[Candle]:
        """Returns reference to the managed candles list.

        WARNING: This is a live reference, not a copy. Modifications affect
        all indicators sharing this manager. This is intentional to enable
        indicator chaining (e.g., one indicator reading another's results).
        """
        if self.candlestick:
            return self.candlestick.derived_candles
        return self._candles

    @candles.setter
    def candles(self, candles: list[Candle]):
        """Set the Candles by clearing and extending (preserves reference)"""
        self._candles.clear()
        self._candles.extend(candles)
        if self.candlestick:
            self.candlestick.derived_candles.reset()

    def _candle_tasks(
        self,
        mode: CalcMode = CalcMode.INSERT,
        index: int | None = None,
    ):
        self.resample_candles(mode, index)
        self.candlestick_conversion(mode, index)
        self.trim_candles()

    def find_indicator(self, name: str) -> bool:
        return any(reading_by_candle(candle, name) for candle in reversed(self.candles))

    def _accepts_candle(self, candle: Candle) -> bool:
        """Route candles to managers by label: skip unlabeled or coarser-than-manager bars."""
        if not self.timeframe:
            return True
        if not candle.timeframe:
            return False
        return candle.timeframe <= self.timeframe

    def prepend(self, candles: Candles):
        self._prepend_parsed(parse_candles(candles))

    def _store_candle(self, candle: Candle, admitted: set[int] | None) -> Candle:
        return candle.admit_for_storage(
            admitted, force_copy=self.timeframe is not None
        )

    def _prepend_parsed(
        self, candles_: list[Candle], admitted: set[int] | None = None
    ):
        self.sort_candles(candles_)

        changed = False
        for candle in reversed(candles_):
            if not self._accepts_candle(candle):
                continue

            self._candles.insert(0, self._store_candle(candle, admitted))
            changed = True

        if changed:
            self._candle_tasks(CalcMode.PREPEND)

    def append(self, candles: Candles):
        self._append_parsed(parse_candles(candles))

    def _append_parsed(
        self, candles_: list[Candle], admitted: set[int] | None = None
    ):
        index = len(self._candles) - 1 if len(self._candles) > 0 else 0

        changed = False
        for candle in candles_:
            if not self._accepts_candle(candle):
                continue

            self._candles.append(self._store_candle(candle, admitted))
            changed = True

        if changed:
            self._candle_tasks(CalcMode.APPEND, index)

    def insert(self, candles: Candles):
        self._insert_parsed(parse_candles(candles))

    def _insert_parsed(
        self, candles_: list[Candle], admitted: set[int] | None = None
    ):
        self.sort_candles(candles_)

        to_sort = False
        last_timestamp = self._candles[-1].timestamp if self._candles else None
        changed = False

        for candle in candles_:
            if not self._accepts_candle(candle):
                continue

            if last_timestamp and candle.timestamp and candle.timestamp < last_timestamp:
                to_sort = True

            self._candles.append(self._store_candle(candle, admitted))
            changed = True

        if not changed:
            return

        if to_sort:
            self.sort_candles()

        self._candle_tasks(CalcMode.INSERT)

    def sort_candles(self, candles: list[Candle] | None = None):
        """Sorts Candles in order of timestamp, accounts for collapsing"""
        if candles:
            target = candles
        else:
            target = self._candles

        if not self.timeframe:
            target.sort(
                key=lambda c: (
                    c.timestamp is None,
                    c.timestamp.timestamp() if c.timestamp else 0.0,
                )
            )
        else:
            target.sort(key=cmp_to_key(self._sort_comparison))

    def _sort_comparison(self, candle_one: Candle, candle_two: Candle) -> int:
        """Sort's Candles in order but if timeframe exists, sorts with collapsing in mind.
        So mixed order of candles will arrange for candles to be resampled down based on given timeframe
        EG:
            No Timeframe : [09:05:00 09:02:00 09:10:00] > [09:02:00 09:05:00 09:10:00]
            T5 Timeframe : [09:05:00 09:02:00 09:10:00] > [09:05:00 09:02:00 09:10:00]
        """
        if candle_one.timestamp is None and candle_two.timestamp is None:
            return 0
        if candle_one.timestamp is None:
            return 1
        if candle_two.timestamp is None:
            return -1

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

        last_candle = self._candles[-1]
        if last_candle.timestamp is None:
            return

        cutoff_time = last_candle.timestamp - self.candle_life

        keep_index = 0
        for i, candle in enumerate(self._candles):
            if candle.timestamp is None or candle.timestamp >= cutoff_time:
                keep_index = i
                break

        if keep_index > 0:
            del self._candles[:keep_index]

    def resample_candles(
        self,
        mode: CalcMode,
        index: int | None = None,
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

        to_process = self._candles[start_index:end_index]

        # Optimization: Skip resampling for INSERT mode if all candles already properly formatted
        # For APPEND/PREPEND, we still need to run resample for gap filling
        # Also skip optimization if timeframe_fill is True as we need to check for gaps
        if (
            mode == CalcMode.INSERT
            and not self.timeframe_fill
            and to_process
            and all(c.timeframe == self.timeframe for c in to_process)
        ):
            timestamps_sorted = True
            for i in range(len(to_process) - 1):
                t1 = to_process[i].timestamp
                t2 = to_process[i + 1].timestamp
                if t1 is None or t2 is None:
                    continue
                if t1 > t2:
                    timestamps_sorted = False
                    break

            if timestamps_sorted:
                return

        del self._candles[start_index:end_index]

        candles_ = [to_process[0]]

        init_candle = candles_[0]
        init_candle.timeframe = self.timeframe
        if not init_candle.timestamp:
            return

        start_time = round_down_timestamp(init_candle.timestamp, self.timeframe)
        end_time = start_time + self.timeframe

        if not on_timeframe(init_candle.timestamp, self.timeframe):
            init_candle.set_resampled_timestamp(end_time)

        for i, candle in enumerate(to_process[1:], start=1):
            prev_candle = candles_[-1]

            if not candle.timestamp:
                return

            if (
                mode != CalcMode.INSERT
                and candle.timeframe == self.timeframe
                and prev_candle.timeframe == self.timeframe
            ):
                candles_.append(candle)
                candles_.extend(to_process[i + 1 :])
                break

            next_end_time = end_time + self.timeframe
            candle.timestamp = candle.timestamp.replace(microsecond=0)
            candle.timeframe = self.timeframe

            if (
                start_time < candle.timestamp <= end_time
                and prev_candle.timestamp == end_time
            ) or (
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
            elif start_time < candle.timestamp and on_timeframe(
                candle.timestamp, self.timeframe
            ):
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
        candles: list[Candle],
        timeframe: timedelta,
        start_index: int = 0,
        end_index: int | None = None,
    ) -> list[Candle]:
        """Generates filler Candle's to the list of Candles.
        Filler Candles are Candles that fill gaps of timeframed Candles,
        which are simply filled with previous Candle's 'close' value."""
        if len(candles) < 2:
            return candles

        result = []
        start_idx = start_index if start_index != 0 else 1
        end_idx = end_index if end_index else len(candles)

        # Add candles before start_idx
        result.extend(candles[:start_idx])

        for i in range(start_idx, min(end_idx, len(candles))):
            prev_candle = result[-1]

            if prev_candle.timestamp is None:
                result.extend(candles[i:])
                break

            current_candle = candles[i]

            # Fill gaps between prev_candle and current_candle
            expected_timestamp = prev_candle.timestamp + timeframe
            while expected_timestamp < current_candle.timestamp:
                fill_candle = Candle(
                    open=prev_candle.close,
                    close=prev_candle.close,
                    high=prev_candle.close,
                    low=prev_candle.close,
                    volume=0,
                    timestamp=expected_timestamp,
                    timeframe=prev_candle.timeframe,
                )
                fill_candle.aggregation_factor = 0
                result.append(fill_candle)
                prev_candle = fill_candle
                expected_timestamp = prev_candle.timestamp + timeframe

            # Add the current candle
            result.append(current_candle)

        return result

    def candlestick_conversion(self, mode: CalcMode, index: int | None = None):
        if self.candlestick:
            self.candlestick.transform(mode, index)

    def purge(self, indicator: str | set[str]):
        """Remove this indicator value from all Candles"""
        if isinstance(indicator, str):
            indicator = {indicator}

        for candle in self.candles:
            for name in indicator:
                candle.indicators.pop(name, None)
                candle.sub_indicators.pop(name, None)
