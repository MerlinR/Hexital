from hexital.candlesticks import CANDLESTICK_MAP
from hexital.core.candlestick_type import CandlestickType
from hexital.exceptions import InvalidCandlestickType


def validate_candlesticktype(
    candlestick_type: CandlestickType | str | None,
) -> CandlestickType | None:
    if isinstance(candlestick_type, CandlestickType):
        return candlestick_type
    elif isinstance(candlestick_type, str):
        if not CANDLESTICK_MAP.get(candlestick_type):
            raise InvalidCandlestickType(f"Candlestick type {candlestick_type} is Invalid")
        requested_candlesticks = CANDLESTICK_MAP[candlestick_type]
        return requested_candlesticks()

    return None
