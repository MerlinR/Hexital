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
    def from_dict(cls, value: Dict[str, float]) -> OHLCV:
        return cls(
            value.get("open", 0.0),
            value.get("high", 0.0),
            value.get("low", 0.0),
            value.get("close", 0.0),
            value.get("volume", 0.0),
        )

    @staticmethod
    def from_dicts(values: List[Dict[str, float]]) -> List[OHLCV]:
        return [OHLCV.from_dict(value) for value in values]
