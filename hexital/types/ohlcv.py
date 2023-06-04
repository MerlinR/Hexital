from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class Candle:
    open: float = 0.0
    high: float = 0.0
    low: float = 0.0
    close: float = 0.0
    volume: int = 0
    indicators: Dict[str, float | dict] = field(default_factory=dict)
    sub_indicators: Dict[str, float | dict] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, value: Dict[str, float]) -> Candle:
        return cls(
            value.get("open", 0.0),
            value.get("high", 0.0),
            value.get("low", 0.0),
            value.get("close", 0.0),
            value.get("volume", 0.0),
        )

    @staticmethod
    def from_dicts(values: List[Dict[str, float]]) -> List[Candle]:
        return [Candle.from_dict(value) for value in values]
