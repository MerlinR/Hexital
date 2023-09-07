from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class OHLCV:
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    close: Optional[float] = None
    volume: Optional[int] = None
    indicators: Dict[str, float | dict] = field(default_factory=dict)
    sub_indicators: Dict[str, float | dict] = field(default_factory=dict)
    timestamp: datetime = None

    @classmethod
    def from_dict(cls, candle: Dict[str, float]) -> OHLCV:
        """Expected dict with keys ['open', 'high', 'low', 'close', 'volume']
        with optional 'timestamp' key."""
        return cls(
            candle.get("open", 0.0),
            candle.get("high", 0.0),
            candle.get("low", 0.0),
            candle.get("close", 0.0),
            candle.get("volume", 0),
            timestamp=candle.get("timestamp"),
        )

    @staticmethod
    def from_dicts(candles: List[Dict[str, float]]) -> List[OHLCV]:
        """Expected list of dict's with keys ['open', 'high', 'low', 'close', 'volume']
        with optional 'timestamp' key."""
        return [OHLCV.from_dict(candle) for candle in candles]

    @classmethod
    def from_list(cls, candle: List[float]) -> OHLCV:
        """Expected list [open, high, low, close, volume]
        with optional datetime at the begining or end."""
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

    @classmethod
    def from_lists(cls, candles: List[List[float]]) -> List[OHLCV]:
        """Expected list of the folling list [open, high, low, close, volume]
        with optional datetime at the begining or end."""
        return [OHLCV.from_list(candle) for candle in candles]
