from __future__ import annotations

from dataclasses import dataclass, field
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

    @classmethod
    def from_dict(cls, candle: Dict[str, float]) -> OHLCV:
        return cls(
            candle.get("open", 0.0),
            candle.get("high", 0.0),
            candle.get("low", 0.0),
            candle.get("close", 0.0),
            candle.get("volume", 0),
        )

    @staticmethod
    def from_dicts(candles: List[Dict[str, float]]) -> List[OHLCV]:
        return [OHLCV.from_dict(candle) for candle in candles]
