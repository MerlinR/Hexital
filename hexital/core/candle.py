from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class Candle:
    open: float
    high: float
    low: float
    close: float
    volume: int
    indicators: Dict[str, float | Dict[str, float | None] | None] = field(default_factory=dict)
    sub_indicators: Dict[str, float | Dict[str, float | None] | None] = field(default_factory=dict)
    timestamp: Optional[datetime] = None

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
        """Expected list of the folling list [open, high, low, close, volume]
        with optional datetime at the begining or end."""
        return [Candle.from_list(candle) for candle in candles]

    def merge(self, candle: Candle):
        """Merge candle into existing candle, will use the merged into
        Candle for any already calc indicators"""
        ignored_keys = ["timestamp", "open"]

        for key, val in vars(candle).items():
            if key in ignored_keys:
                continue

            if key == "high":
                self.high = max(self.high, val)
            elif key == "low":
                self.low = min(self.low, val)
            elif key == "volume":
                self.volume += val
            elif isinstance(val, dict):
                setattr(self, key, {})
            elif val is not None:
                setattr(self, key, val)
