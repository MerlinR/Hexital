from __future__ import annotations

from datetime import datetime, timedelta
from functools import cmp_to_key
from typing import Literal

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
        appended_count: int = 0,
    ):
        self.resample_candles(mode, index, appended_count)
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
        return candle.admit_for_storage(admitted, force_copy=self.timeframe is not None)

    def _prepend_parsed(self, candles_: list[Candle], admitted: set[int] | None = None):
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

    def _append_parsed(self, candles_: list[Candle], admitted: set[int] | None = None):
        index = len(self._candles) - 1 if len(self._candles) > 0 else 0

        changed = False
        appended_count = 0
        for candle in candles_:
            if not self._accepts_candle(candle):
                continue

            self._candles.append(self._store_candle(candle, admitted))
            changed = True
            appended_count += 1

        if changed:
            self._candle_tasks(CalcMode.APPEND, index, appended_count)

    def insert(self, candles: Candles):
        self._insert_parsed(parse_candles(candles))

    def _insert_parsed(self, candles_: list[Candle], admitted: set[int] | None = None):
        self.sort_candles(candles_)

        to_sort = False
        last_timestamp = self._candles[-1].timestamp if self._candles else None
        changed = False

        for candle in candles_:
            if not self._accepts_candle(candle):
                continue

            if (
                last_timestamp
                and candle.timestamp
                and candle.timestamp < last_timestamp
            ):
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
        appended_count: int = 0,
    ):
        """Resample candles into the manager timeframe."""
        tf = self.timeframe
        if not tf:
            return

        if not self.timeframe_fill:
            if mode == CalcMode.APPEND and appended_count >= 1:
                if appended_count == 1 and self._try_resample_append_inplace():
                    return
                if appended_count > 1 and self._try_resample_multi_append(
                    appended_count
                ):
                    return

        if mode == CalcMode.INSERT:
            start_index = 0
        elif index is not None:
            start_index = index
        else:
            start_index = self._find_resample_index()

        end_index = len(self._candles)
        if end_index <= start_index + 1:
            return

        if not self.timeframe_fill and self._range_already_resampled(
            start_index, end_index
        ):
            return

        self._resample_rebuild_range(start_index, end_index, mode)

    def _candle_bounds(self, timestamp: datetime) -> tuple[datetime, datetime]:
        start = round_down_timestamp(timestamp, self.timeframe)
        return start, start + self.timeframe

    def _slot_first_resampled(self, candle: Candle, incoming_ts: datetime) -> None:
        tf = self.timeframe
        candle.timeframe = tf

        if not on_timeframe(incoming_ts, tf):
            slot = round_down_timestamp(incoming_ts, tf)
            candle.set_resampled_timestamp(slot + tf)
        else:
            candle.timestamp = incoming_ts

    def _apply_resample_step(
        self,
        prev: Candle,
        incoming: Candle,
        incoming_ts: datetime,
    ) -> Literal["merge", "slot"] | None:
        """Merge or slot incoming against a resampled prev bar. None => full rebuild needed."""
        tf = self.timeframe
        start_time, end_time = self._candle_bounds(prev.timestamp)

        if (start_time < incoming_ts <= end_time and prev.timestamp == end_time) or (
            start_time - tf < incoming_ts <= start_time and prev.timestamp == start_time
        ):
            incoming.timeframe = tf
            prev.merge(incoming)
            return "merge"

        if start_time < incoming_ts <= end_time:
            incoming.timeframe = tf
            incoming.set_resampled_timestamp(end_time)
            return "slot"

        next_end_time = end_time + tf
        if end_time < incoming_ts <= next_end_time:
            incoming.timeframe = tf
            incoming.set_resampled_timestamp(next_end_time)
            return "slot"

        if start_time < incoming_ts and on_timeframe(incoming_ts, tf):
            slot = round_down_timestamp(incoming_ts, tf)
            incoming.timeframe = tf
            incoming.set_resampled_timestamp(slot)
            return "slot"

        if next_end_time < incoming_ts:
            slot = round_down_timestamp(incoming_ts, tf)
            incoming.timeframe = tf
            incoming.set_resampled_timestamp(slot + tf)
            return "slot"

        return None

    def _range_already_resampled(self, start_index: int, end_index: int) -> bool:
        tf = self.timeframe
        candles = self._candles

        for i in range(start_index, end_index):
            if candles[i].timeframe != tf:
                return False

        for i in range(start_index, end_index - 1):
            t1 = candles[i].timestamp
            t2 = candles[i + 1].timestamp
            if t1 is None or t2 is None:
                continue
            if t1 > t2:
                return False

        return True

    def _resample_rebuild_range(self, start_index: int, end_index: int, mode: CalcMode):
        tf = self.timeframe
        to_process = self._candles[start_index:end_index]
        del self._candles[start_index:]

        candles_ = [to_process[0]]
        init_candle = candles_[0]
        if not init_candle.timestamp:
            return

        self._slot_first_resampled(
            init_candle, init_candle.timestamp.replace(microsecond=0)
        )

        for i in range(1, len(to_process)):
            candle = to_process[i]
            prev_candle = candles_[-1]

            if not candle.timestamp:
                return

            if (
                mode != CalcMode.INSERT
                and candle.timeframe == tf
                and prev_candle.timeframe == tf
            ):
                candles_.append(candle)
                candles_.extend(to_process[i + 1 :])
                break

            incoming_ts = candle.timestamp.replace(microsecond=0)

            if prev_candle.timeframe == tf:
                step = self._apply_resample_step(prev_candle, candle, incoming_ts)
                if step == "merge":
                    continue
                if step == "slot":
                    candles_.append(candle)
                    continue

            raise InvalidCandleOrder(
                f"Failed to resample_candles due to invalid candle order prev: [{prev_candle}] - current: [{candle}]",
            )

        if self.timeframe_fill:
            candles_ = self._fill_timeframe_candles(
                candles_, tf, start_index, end_index
            )

        self._candles.extend(candles_)

    def _try_resample_append_inplace(self) -> bool:
        """Fast path for a single appended candle: merge or slot without tail rebuild."""
        candles = self._candles
        tf = self.timeframe
        if len(candles) < 1:
            return False

        incoming = candles[-1]
        if not incoming.timestamp:
            return False

        incoming_ts = incoming.timestamp.replace(microsecond=0)

        if len(candles) >= 2:
            prev = candles[-2]
            if incoming.timeframe == tf and prev.timeframe == tf:
                return True

            if prev.timeframe != tf:
                return False

            step = self._apply_resample_step(prev, incoming, incoming_ts)
            if step == "merge":
                candles.pop()
            elif step is None:
                return False
            return True

        if incoming.timeframe == tf:
            return True

        self._slot_first_resampled(incoming, incoming_ts)
        return True

    def _try_resample_multi_append(self, appended_count: int) -> bool:
        """In-place resample when several candles were appended in one call."""
        candles = self._candles
        tf = self.timeframe
        length = len(candles)

        if length < appended_count + 1:
            return False

        prev_idx = length - appended_count - 1
        prev = candles[prev_idx]
        if prev.timeframe != tf:
            return False

        idx = prev_idx + 1
        while idx < len(candles):
            incoming = candles[idx]
            if incoming.timeframe == tf:
                idx += 1
                prev = incoming
                continue
            if not incoming.timestamp:
                return False

            incoming_ts = incoming.timestamp.replace(microsecond=0)
            step = self._apply_resample_step(prev, incoming, incoming_ts)
            if step == "merge":
                candles.pop(idx)
                continue
            if step == "slot":
                prev = incoming
                idx += 1
                continue
            return False

        return True

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
