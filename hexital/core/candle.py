from __future__ import annotations

try:
    from datetime import UTC
except ImportError:
    UTC = False

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from hexital.exceptions import CandleAlreadyTagged
from hexital.utils.timeframe import TimeFrame, convert_timeframe_to_timedelta

IGNORE_CLEAN = ["indicators", "sub_indicators", "_clean_values", "_tag"]


class Candle:
    open: float
    high: float
    low: float
    close: float
    volume: int
    timestamp: datetime
    indicators: Dict[str, float | Dict[str, float | None] | None]
    sub_indicators: Dict[str, float | Dict[str, float | None] | None]
    timeframe: Optional[timedelta]
    aggregation_factor: int = 1
    _clean_values: Dict[str, float | int]
    _tag: Optional[str] = None
    _start_timestamp: Optional[datetime] = None
    _end_timestamp: Optional[datetime] = None

    def __init__(
        self,
        open: float,
        high: float,
        low: float,
        close: float,
        volume: int,
        timestamp: Optional[datetime | str] = None,
        timeframe: Optional[str | TimeFrame | timedelta | int] = None,
        indicators: Optional[Dict[str, float | Dict[str, float | None] | None]] = None,
        sub_indicators: Optional[Dict[str, float | Dict[str, float | None] | None]] = None,
    ):
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume
        self.timeframe = convert_timeframe_to_timedelta(timeframe) if timeframe else None

        if isinstance(timestamp, datetime):
            self.timestamp = timestamp
        elif isinstance(timestamp, str):
            self.timestamp = datetime.fromisoformat(timestamp)
        else:
            if UTC:
                self.timestamp = datetime.now(UTC)
            else:
                self.timestamp = datetime.utcnow()

        self._clean_values = {}
        self.indicators = indicators if indicators else {}
        self.sub_indicators = sub_indicators if sub_indicators else {}

    def __eq__(self, other) -> bool:
        if not isinstance(other, Candle):
            return False
        for key in self.__dict__.keys():
            if key in ["_start_timestamp", "_end_timestamp", "timeframe"]:
                local = getattr(self, key)
                remote = getattr(other, key)
                if remote is not None and local is not None and remote != local:
                    return False
            elif key.startswith("_"):
                continue
            elif getattr(self, key) != getattr(other, key):
                return False
        return True

    def __repr__(self) -> str:
        return str({name: value for name, value in vars(self).items() if not name.startswith("_")})

    @property
    def tag(self) -> str | None:
        return self._tag

    @tag.setter
    def tag(self, tag: str):
        if not self._tag:
            self._tag = tag
            return
        raise CandleAlreadyTagged(f"Candle already tagged as {self._tag} - [{self}]")

    @property
    def positive(self) -> bool:
        return self.open < self.close

    @property
    def negative(self) -> bool:
        return self.open > self.close

    @property
    def realbody(self) -> float:
        return abs(self.open - self.close)

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

    @classmethod
    def from_dict(cls, candle: Dict[str, Any]) -> Candle:
        """
        Create a `Candle` object from a dictionary representation.

        The dictionary is expected to have the following keys:
        - Required: 'open', 'high', 'low', 'close', 'volume'
        - Optional: 'timestamp', 'time', 'date'
        - Optional: 'timeframe'

        The method extracts the values for these keys. If the optional keys for time ('timestamp',
        'time', etc.) are present, the first match is used as the timestamp.

        Args:
            candle (Dict[str, Any]): A dictionary containing the candle data.

        Returns:
            Candle: A `Candle` object initialized with the provided dictionary data.
        """
        time = [
            v
            for k, v in candle.items()
            if k in ["timestamp", "Timestamp", "time", "Time", "date", "Date"]
        ]
        return cls(
            candle.get("open", candle.get("Open", 0.0)),
            candle.get("high", candle.get("High", 0.0)),
            candle.get("low", candle.get("Low", 0.0)),
            candle.get("close", candle.get("Close", 0.0)),
            candle.get("volume", candle.get("Volume", 0)),
            timestamp=time[0] if time else None,
            timeframe=candle.get("timeframe", candle.get("Timeframe")),
        )

    @staticmethod
    def from_dicts(candles: List[Dict[str, float]]) -> List[Candle]:
        """
        Create's a list of `Candle` object's from a list of dictionary representation.

        Each dictionary is expected to have the following keys:
        - Required: 'open', 'high', 'low', 'close', 'volume'
        - Optional: 'timestamp', 'time', 'date'
        - Optional: 'timeframe'

        The method extracts the values for these keys. If the optional keys for time ('timestamp',
        'time', etc.) are present, the first match is used as the timestamp.
        Returning a list of `Candle` objects initialized with the provided dictionary data.

        Args:
            candles (List[Dict[str, Any]]): A dictionary containing the candle data.

        Returns:
            List[Candle]: A list of `Candle` object's.
        """
        return [Candle.from_dict(candle) for candle in candles]

    @classmethod
    def from_list(cls, candle: list) -> Candle:
        """
        Create a `Candle` object from a list representation.

        The list is expected to contain the following elements:
        - Required: `[open, high, low, close, volume]` in that order.
        - Optional: A `timestamp` at the beginning of the list.
        - Optional: A `timeframe` at the end of the list.

        If the first element is a `str` or `datetime`, it is treated as the `timestamp`.
        If the last element is a `str`, `int`, `TimeFrame`, or `timedelta`, it is treated as the `timeframe`.

        Args:
            candle (list): A list containing the candle data.

        Returns:
            Candle: A `Candle` object initialized with the data from the list.
        """
        timestamp = None
        timeframe = None

        if len(candle) > 5 and isinstance(candle[0], (str, datetime)):
            timestamp = candle.pop(0)
        if len(candle) > 5 and isinstance(candle[-1], (str, int, TimeFrame, timedelta)):
            timeframe = candle.pop(-1)

        return cls(
            open=candle[0],
            high=candle[1],
            low=candle[2],
            close=candle[3],
            volume=candle[4],
            timestamp=timestamp,
            timeframe=timeframe,
        )

    @staticmethod
    def from_lists(candles: List[list]) -> List[Candle]:
        """
        Create a list of `Candle` object's from a list of list representation.

        Each list is expected to contain the following elements:
        - Required: `[open, high, low, close, volume]` in that order.
        - Optional: A `timestamp` at the beginning of the list.
        - Optional: A `timeframe` at the end of the list.

        If the first element is a `str` or `datetime`, it is treated as the `timestamp`.
        If the last element is a `str`, `int`, `TimeFrame`, or `timedelta`, it is treated as the `timeframe`.

        Args:
            candles (List[list]): A list of list's containing the candle data.

        Returns:
            List[Candle]: A list of `Candle` object's.
        """
        return [Candle.from_list(candle) for candle in candles]

    def set_collapsed_timestamp(self, timestamp: datetime):
        if not self._start_timestamp:
            self._start_timestamp = self.timestamp
        self.timestamp = timestamp

    def save_clean_values(self):
        self._clean_values = {
            name: value for name, value in vars(self).items() if name not in IGNORE_CLEAN
        }

    def recover_clean_values(self):
        if self._clean_values:
            for name, value in self._clean_values.items():
                self.__setattr__(name, value)
        self._clean_values = {}

    def reset_candle(self):
        self.indicators = {}
        self.sub_indicators = {}
        self._tag = None

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

        if self.timeframe:
            if (candle.timestamp + self.timeframe > self.timestamp + self.timeframe) or (
                candle.timestamp < self.timestamp - self.timeframe
            ):
                return

        self.recover_clean_values()

        if self._start_timestamp and candle.timestamp < self._start_timestamp:
            self.open = candle.open
            if not self._end_timestamp:
                self._end_timestamp = self._start_timestamp
            self._start_timestamp = candle.timestamp
        elif (
            self._start_timestamp
            and not self._end_timestamp
            and candle.timestamp > self._start_timestamp
        ):
            self.close = candle.close
            self._end_timestamp = candle.timestamp
        elif (
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
