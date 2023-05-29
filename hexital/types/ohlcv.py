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
    hex_ta: Dict[str, float] = field(default_factory=dict)

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
    def from_dicts(values: List[Dict[str, float]]) -> Candle:
        return [
            Candle(
                value.get("open", 0.0),
                value.get("high", 0.0),
                value.get("low", 0.0),
                value.get("close", 0.0),
                value.get("volume", 0.0),
            )
            for value in values
        ]
