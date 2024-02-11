from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from hexital.exceptions import CandleAlreadyTagged

KEY_KEYS = [
    "open",
    "high",
    "low",
    "close",
    "volume",
    "timestamp",
    "indicators",
    "sub_indicators",
]


class Candle:
    open: float
    high: float
    low: float
    close: float
    volume: int
    timestamp: Optional[datetime] = None
    clean_values: Dict[str, float | int]
    _tag: Optional[str] = None
    indicators: Dict[str, float | Dict[str, float | None] | None]
    sub_indicators: Dict[str, float | Dict[str, float | None] | None]

    def __init__(
        self,
        open: float,
        high: float,
        low: float,
        close: float,
        volume: int,
        timestamp: Optional[datetime | str] = None,
        indicators: Optional[Dict[str, float | Dict[str, float | None] | None]] = None,
        sub_indicators: Optional[Dict[str, float | Dict[str, float | None] | None]] = None,
    ):
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume

        if isinstance(timestamp, datetime):
            self.timestamp = timestamp
        elif isinstance(timestamp, str):
            self.timestamp = datetime.fromisoformat(timestamp)

        self.clean_values = {}
        self.indicators = indicators if indicators else {}
        self.sub_indicators = sub_indicators if sub_indicators else {}

    def __eq__(self, other) -> bool:
        if not isinstance(other, Candle):
            return False
        for key in KEY_KEYS:
            if getattr(self, key) != getattr(other, key):
                return False
        return True

    def __repr__(self) -> str:
        return str(
            {
                "open": self.open,
                "high": self.high,
                "low": self.low,
                "close": self.close,
                "volume": self.volume,
                "timestamp": self.timestamp,
                "indicators": self.indicators,
                "sub_indicators": self.sub_indicators,
                "tag": self.tag,
            }
        )

    @property
    def tag(self) -> str | None:
        return self._tag

    @tag.setter
    def tag(self, tag: str):
        if not self._tag:
            self._tag = tag
            return
        raise CandleAlreadyTagged(f"Candle already tagged as {self._tag} - [{self}]")

    def positive(self) -> bool:
        return self.open < self.close

    def negative(self) -> bool:
        return self.open > self.close

    def realbody(self) -> float:
        return abs(self.open - self.close)

    def shadow_upper(self) -> float:
        if self.positive():
            return abs(self.high - self.close)
        return abs(self.high - self.open)

    def shadow_lower(self) -> float:
        if self.positive():
            return abs(self.low - self.open)
        return abs(self.low - self.close)

    def high_low(self) -> float:
        return abs(self.high - self.low)

    @classmethod
    def from_dict(cls, candle: Dict[str, Any]) -> Candle:
        """Expected dict with keys ['open', 'high', 'low', 'close', 'volume']
        with optional 'timestamp' key."""
        return cls(
            candle.get("open", candle.get("Open", 0.0)),
            candle.get("high", candle.get("High", 0.0)),
            candle.get("low", candle.get("Low", 0.0)),
            candle.get("close", candle.get("Close", 0.0)),
            candle.get("volume", candle.get("Volume", 0)),
            timestamp=candle.get("timestamp", candle.get("Timestamp")),
        )

    @staticmethod
    def from_dicts(candles: List[Dict[str, float]]) -> List[Candle]:
        """Expected list of dict's with keys ['open', 'high', 'low', 'close', 'volume']
        with optional 'timestamp' key."""
        return [Candle.from_dict(candle) for candle in candles]

    @classmethod
    def from_list(cls, candle: list) -> Candle:
        """Expected list [open, high, low, close, volume]
        with optional datetime at the beginning or end."""
        timestamp = None
        if isinstance(candle[0], datetime):
            timestamp = candle.pop(0)
        elif isinstance(candle[-1], datetime):
            timestamp = candle.pop(-1)

        return cls(
            open=candle[0],
            high=candle[1],
            low=candle[2],
            close=candle[3],
            volume=candle[4],
            timestamp=timestamp,
        )

    @staticmethod
    def from_lists(candles: List[List[float]]) -> List[Candle]:
        """Expected list of the following list [open, high, low, close, volume]
        with optional datetime at the beginning or end."""
        return [Candle.from_list(candle) for candle in candles]

    def save_clean_values(self):
        self.clean_values = {
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume,
        }

    def recover_clean_values(self):
        if self.clean_values:
            self.open = self.clean_values["open"]
            self.high = self.clean_values["high"]
            self.low = self.clean_values["low"]
            self.close = self.clean_values["close"]
            self.volume = int(self.clean_values["volume"])

    def reset_candle(self):
        self.indicators = {}
        self.sub_indicators = {}
        self._tag = None

    def merge(self, candle: Candle):
        """Merge candle into existing candle, will use the merged into
        Candle for any already calc indicators.
        All indicators will be wiped due to new values, and any conversion removed"""

        self.recover_clean_values()

        self.high = max(self.high, candle.high)
        self.low = min(self.low, candle.low)
        self.volume += candle.volume
        self.close = candle.close

        self.clean_values = {}
        self.reset_candle()
