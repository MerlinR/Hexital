from hexital.candlesticks import CANDLESTICK_MAP
from hexital.core.candlestick_type import CandlestickType
from hexital.exceptions import InvalidCandlestickType


def validate_candlesticktype(
    candlestick: CandlestickType | str,
) -> CandlestickType:
    if isinstance(candlestick, CandlestickType):
        return candlestick

    if not CANDLESTICK_MAP.get(candlestick):
        raise InvalidCandlestickType(f"Candlestick type {candlestick} is Invalid")

    requested_candlesticks = CANDLESTICK_MAP[candlestick]
    return requested_candlesticks()
