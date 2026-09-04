from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime, timedelta
from typing import Any

from ..utils.timeframe import (
    TimeFramesSource,
    convert_timeframe_to_timedelta,
)
from . import Reading


class Candle:
    open: float
    high: float
    low: float
    close: float
    volume: int
    timestamp: datetime | None
    indicators: dict[str, Reading]
    sub_indicators: dict[str, Reading]
    timeframe: timedelta | None
    aggregation_factor: int
    tag: str | None = None
    refs: dict[str, Sequence | None]
    _start_timestamp: datetime | None = None
    _end_timestamp: datetime | None = None

    def __init__(
        self,
        open: float,
        high: float,
        low: float,
        close: float,
        volume: int,
        timestamp: datetime | str | None = None,  # End of Candle
        timeframe: TimeFramesSource | None = None,
        indicators: dict[str, Reading] | None = None,
        sub_indicators: dict[str, Reading] | None = None,
        aggregation_factor: int | None = None,
    ):
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume
        self.timeframe = convert_timeframe_to_timedelta(timeframe) if timeframe else None

        self.tag = None
        self.aggregation_factor = (
            aggregation_factor if aggregation_factor is not None else 1
        )

        if isinstance(timestamp, datetime):
            self.timestamp = timestamp
        elif isinstance(timestamp, str):
            self.timestamp = datetime.fromisoformat(timestamp)
        else:
            self.timestamp = None

        self.refs = {}
        self.indicators = indicators if indicators else {}
        self.sub_indicators = sub_indicators if sub_indicators else {}

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Candle):
            return False

        lenient_keys = {"_start_timestamp", "_end_timestamp", "timeframe"}
        keys = set(self.__dict__) | set(other.__dict__)

        for key in keys:
            if key.startswith("_") and key not in lenient_keys:
                continue

            value = getattr(self, key, None)
            other_value = getattr(other, key, None)

            if key in lenient_keys:
                if value is not None and other_value is not None and value != other_value:
                    return False
                continue

            if value != other_value:
                return False

        return True

    def __repr__(self) -> str:
        return str(
            {
                name: value
                for name, value in vars(self).items()
                if not name.startswith("_")
            }
        )

    @property
    def positive(self) -> bool:
        return self.open < self.close

    @property
    def negative(self) -> bool:
        return self.open > self.close

    @property
    def white_body(self) -> bool:
        return self.close >= self.open

    @property
    def black_body(self) -> bool:
        return self.close < self.open

    @property
    def realbody(self) -> float:
        return abs(self.open - self.close)

    @property
    def realbody_high(self) -> float:
        return max(self.open, self.close)

    @property
    def realbody_low(self) -> float:
        return min(self.open, self.close)

    @property
    def shadow_upper(self) -> float:
        if self.positive:
            return abs(self.high - self.close)
        return abs(self.high - self.open)

    @property
    def shadow_lower(self) -> float:
        if self.positive:
            return abs(self.low - self.open)
        return abs(self.low - self.close)

    @property
    def high_low(self) -> float:
        return abs(self.high - self.low)

    def as_list(self, readings: bool = False) -> list:
        """
        Generates a list of values from the OHLCV values.
        `[timestamp, open, high, low, close, volume]` in that order.
        With an optional `timedelta` value at the end being the `timeframe`

        Args:
            readings (bool): Include Candle readings

        Returns:
            list: A list of the `Candle` values;
            [timestamp, open, high, low, close, volume, timeframe*]
            [timestamp, open, high, low, close, volume, indicators, sub_indicators, timeframe*]
        """
        cdl = [self.timestamp, self.open, self.high, self.low, self.close, self.volume]

        if readings:
            cdl.append(self.indicators)
            cdl.append(self.sub_indicators)

        cdl += [self.timeframe] if self.timeframe else []

        return cdl

    def as_dict(self, readings: bool = False) -> dict:
        """
        Generates a dict of values from the OHLCV values, with  the following keys:
        `[timestamp, open, high, low, close, volume]`

        Args:
            readings (bool): Include Candle readings

        Returns:
            dict: A list of the `Candle` values
            {open, high, low, close, volume, timestamp, timeframe*}
            {open, high, low, close, volume, timestamp, indicators, sub_indicators, timeframe*}
        """
        cdl = {
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume,
            "timestamp": self.timestamp,
        }

        if self.timeframe:
            cdl["timeframe"] = self.timeframe

        if readings:
            cdl["indicators"] = self.indicators
            cdl["sub_indicators"] = self.sub_indicators

        return cdl

    @classmethod
    def from_dict(
        cls,
        candle: dict[str, Any],
        timeframe: TimeFramesSource | None = None,
    ) -> Candle:
        """
        Create a `Candle` object from a dictionary representation.

        The dictionary is expected to have the following keys:
        - Required: 'open', 'high', 'low', 'close', 'volume'
        - Optional: 'timestamp' | 'time' | 'date'
        - Optional: 'timeframe', 'indicators', 'sub_indicators'

        The method extracts the values for these keys. If the optional keys for time ('timestamp',
        'time', etc.) are present, the first match is used as the timestamp.

        Args:
            candle (Dict[str, Any]): A dictionary containing the candle data.
            timeframe: Optional fallback timeframe used when the dictionary does
                not contain a timeframe field.

        Returns:
            Candle: A `Candle` object initialized with the provided dictionary data.
        """
        timestamp = [
            v
            for k, v in candle.items()
            if k in ["timestamp", "Timestamp", "time", "Time", "date", "Date"]
        ]

        if timestamp and not isinstance(timestamp[0], (datetime, str)):
            raise TypeError("Timestamp must be native python Datetime object")

        candle_timeframe = candle.get("timeframe", candle.get("Timeframe", timeframe))

        return cls(
            candle.get("open", candle.get("Open", 0.0)),
            candle.get("high", candle.get("High", 0.0)),
            candle.get("low", candle.get("Low", 0.0)),
            candle.get("close", candle.get("Close", 0.0)),
            candle.get("volume", candle.get("Volume", 0)),
            indicators=candle.get("indicators", {}),
            sub_indicators=candle.get("sub_indicators", {}),
            timestamp=timestamp[0] if timestamp else None,
            timeframe=candle_timeframe,
        )

    @classmethod
    def from_dicts(
        cls,
        candles: Sequence[dict[str, Any]],
        timeframe: TimeFramesSource | None = None,
    ) -> list[Candle]:
        """
        Create's a list of `Candle` object's from a list of dictionary representation.

        Each dictionary is expected to have the following keys:
        - Required: 'open', 'high', 'low', 'close', 'volume'
        - Optional: 'timestamp' | 'time' | 'date'
        - Optional: 'timeframe', 'indicators', 'sub_indicators'

        The method extracts the values for these keys. If the optional keys for time ('timestamp',
        'time', etc.) are present, the first match is used as the timestamp.
        Returning a list of `Candle` objects initialized with the provided dictionary data.

        Args:
            candles (List[Dict[str, Any]]): A dictionary containing the candle data.
            timeframe: Optional fallback timeframe used when an item does not
                contain a timeframe field.

        Returns:
            List[Candle]: A list of `Candle` object's.
        """
        return [cls.from_dict(candle, timeframe=timeframe) for candle in candles]

    @classmethod
    def from_list(
        cls,
        candle: list,
        timeframe: TimeFramesSource | None = None,
    ) -> Candle:
        """
        Create a `Candle` object from a list representation.

        The list is expected to contain the following elements:
        - Required: `[open, high, low, close, volume]` in that order.
        - Optional: A `timestamp` at the beginning of the list.
        - Optional: A `timeframe` at the end of the list.
        - Optional: Dict's `indicators`, `sub_indicators` after Volume.

        If the first element is a `str` or `datetime`, it is treated as the `timestamp`.
        If the last element is a `str`, `int`, `TimeFrame`, or `timedelta`, it is treated as the `timeframe`.

        Args:
            candle (list): A list containing the candle data.
            timeframe: Optional fallback timeframe used when the list does not
                contain a timeframe value.

        Returns:
            Candle: A `Candle` object initialized with the data from the list.
        """
        candle = list(candle)
        timestamp = None
        candle_timeframe = timeframe
        indicators = {}
        sub_indicators = {}

        if len(candle) > 5 and (
            isinstance(candle[0], (str, datetime)) or candle[0] is None
        ):
            timestamp = candle.pop(0)
        if len(candle) > 5 and isinstance(candle[-1], TimeFramesSource):
            candle_timeframe = candle.pop(-1)
        if (
            len(candle) > 5
            and isinstance(candle[-1], dict)
            and isinstance(candle[-2], dict)
        ):
            sub_indicators = candle.pop(-1)
            indicators = candle.pop(-1)

        return cls(
            open=candle[0],  # type: ignore
            high=candle[1],
            low=candle[2],
            close=candle[3],
            volume=candle[4],
            indicators=indicators,
            sub_indicators=sub_indicators,
            timestamp=timestamp,
            timeframe=candle_timeframe,
        )

    @classmethod
    def from_lists(
        cls,
        candles: list[list],
        timeframe: TimeFramesSource | None = None,
    ) -> list[Candle]:
        """
        Create a list of `Candle` object's from a list of list representation.

        Each list is expected to contain the following elements:
        - Required: `[open, high, low, close, volume]` in that order.
        - Optional: A `timestamp` at the beginning of the list.
        - Optional: A `timeframe` at the end of the list.
        - Optional: Dict's `indicators`, `sub_indicators` after Volume.

        If the first element is a `str` or `datetime`, it is treated as the `timestamp`.
        If the last element is a `str`, `int`, `TimeFrame`, or `timedelta`, it is treated as the `timeframe`.

        Args:
            candles (List[list]): A list of list's containing the candle data.
            timeframe: Optional fallback timeframe used when an item does not
                contain a timeframe value.

        Returns:
            List[Candle]: A list of `Candle` object's.
        """
        return [cls.from_list(candle, timeframe=timeframe) for candle in candles]

    def clean_copy(self) -> Candle:
        """Create a clean copy with OHLCV data but without indicators, refs, or tag."""
        return Candle(
            open=self.open,
            high=self.high,
            low=self.low,
            close=self.close,
            volume=self.volume,
            timestamp=self.timestamp,
            timeframe=self.timeframe,
            aggregation_factor=self.aggregation_factor,
        )

    @property
    def is_clean(self) -> bool:
        """True when the candle has no readings, refs, or tag attached."""
        return not (self.indicators or self.sub_indicators or self.refs or self.tag)

    def admit_for_storage(
        self, admitted: set[int] | None = None, *, force_copy: bool = False
    ) -> Candle:
        """Return a candle safe to store in a CandleManager."""
        if force_copy or not self.is_clean:
            return self.clean_copy()
        if admitted is None:
            return self
        key = id(self)
        if key in admitted:
            return self.clean_copy()
        admitted.add(key)
        return self

    def set_resampled_timestamp(self, timestamp: datetime):
        if not self._start_timestamp:
            self._start_timestamp = self.timestamp
        self.timestamp = timestamp

    def reset_candle(self):
        self.indicators = {}
        self.sub_indicators = {}
        self.refs = {}
        self.tag = None

    def merge(self, candle: Candle):
        """
        Merge another `Candle` object into the current candle.

        This method updates the current candle by integrating data from the provided `candle`.
        It ensures that the merged values respect the timeframe boundaries and adjusts
        attributes such as open, high, low, close, volume, and timestamps accordingly.

        **Note:**
        - Any calculated indicators will be wiped, as merging modifies the core candle values.
        - Any conversion or derived values associated with the candle will also be removed.

        Args:
            candle (Candle): The `Candle` object to merge into the current candle.

        Behaviour:
            - Adjusts the `open` if the merged candle's timestamp is earlier than the start timestamp.
            - Updates the `close` if the merged candle's timestamp is more recent.
            - Updates `high` and `low` based on the maximum and minimum values of the two candles.
            - Increases the `volume` by the volume of the merged candle.
            - Increments the `aggregation_factor` to account for the merged data.
            - Resets calculated indicators and cleans any derived values.
        """
        if self.timestamp is None or candle.timestamp is None:
            self.high = max(self.high, candle.high)
            self.low = min(self.low, candle.low)
            self.close = candle.close
            self.reset_candle()
            return

        if self.timeframe and (
            (candle.timestamp + self.timeframe > self.timestamp + self.timeframe)
            or (candle.timestamp < self.timestamp - self.timeframe)
        ):
            return

        if self._start_timestamp and candle.timestamp < self._start_timestamp:
            self.open = candle.open
            if not self._end_timestamp:
                self._end_timestamp = self._start_timestamp
            self._start_timestamp = candle.timestamp
        elif (
            self._start_timestamp
            and not self._end_timestamp
            and candle.timestamp > self._start_timestamp
        ) or (
            self._start_timestamp
            and self._end_timestamp
            and candle.timestamp > self._end_timestamp
        ):
            self.close = candle.close
            self._end_timestamp = candle.timestamp
        elif (
            self._start_timestamp
            and self._end_timestamp
            and self._start_timestamp > candle.timestamp > self._end_timestamp
        ):
            pass
        else:
            self.close = candle.close

        self.high = max(self.high, candle.high)
        self.low = min(self.low, candle.low)
        self.volume += candle.volume
        self.aggregation_factor += candle.aggregation_factor

        self.reset_candle()
