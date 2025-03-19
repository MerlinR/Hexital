from __future__ import annotations

from typing import Any, List, TypeAlias

from hexital.core.candle import Candle


class NullReadingType:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __repr__(self) -> str:
        return "Null"

    def __eq__(self, value: object, /) -> bool:
        return value is None or isinstance(value, NullReadingType)

    def __bool__(self) -> bool:
        return False


def is_none(obj: Any) -> bool:
    return obj is None or isinstance(obj, NullReadingType)


def is_null(obj: Any) -> bool:
    return isinstance(obj, NullReadingType)


def is_null_conv(obj: Reading | NullReadingType) -> Reading:
    return None if isinstance(obj, NullReadingType) else obj


Reading: TypeAlias = float | dict | bool | None
Candles: TypeAlias = Candle | List[Candle] | dict | List[dict] | list | List[list]

NullReading = NullReadingType()
