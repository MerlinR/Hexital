from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

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
    _open: float
    _high: float
    _low: float
    _close: float
    _volume: int
    timestamp: Optional[datetime] = None
    indicators: Dict[str, float | Dict[str, float | None] | None]
    sub_indicators: Dict[str, float | Dict[str, float | None] | None]

    def __init__(
        self,
        open: float,
        high: float,
        low: float,
        close: float,
        volume: int,
        timestamp: Optional[datetime] = None,
        indicators: Optional[Dict[str, float | Dict[str, float | None] | None]] = None,
        sub_indicators: Optional[Dict[str, float | Dict[str, float | None] | None]] = None,
    ):
        self._open = open
        self._high = high
        self._low = low
        self._close = close
        self._volume = volume
        self.timestamp = timestamp

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
                "open": self._open,
                "high": self._high,
                "low": self._low,
                "close": self._close,
                "volume": self._volume,
                "timestamp": self.timestamp,
                "indicators": self.indicators,
                "sub_indicators": self.sub_indicators,
            }
        )

    @property
    def open(self) -> float:
        return self._open

    @open.setter
    def open(self, open: float):
        self._open = open

    @property
    def high(self) -> float:
        return self._high

    @high.setter
    def high(self, high: float):
        self._high = high

    @property
    def low(self) -> float:
        return self._low

    @low.setter
    def low(self, low: float):
        self._low = low

    @property
    def close(self) -> float:
        return self._close

    @close.setter
    def close(self, close: float):
        self._close = close

    @property
    def volume(self) -> float:
        return self._volume

    @volume.setter
    def volume(self, volume: int):
        self._volume = volume

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

    def merge(self, candle: Candle):
        """Merge candle into existing candle, will use the merged into
        Candle for any already calc indicators"""

        self._high = max(self.high, candle.high)
        self._low = min(self.low, candle.low)
        self._close = candle.close
        self._volume += candle.volume
        self.indicators = {}
        self.sub_indicators = {}
