from ..candlesticks import CANDLESTICK_MAP
from ..core.candlestick_type import CandlestickType
from ..exceptions import InvalidCandlestickType


def validate_candlesticktype(
    candlestick: CandlestickType | str,
) -> CandlestickType:
    if isinstance(candlestick, CandlestickType):
        return candlestick

    if not CANDLESTICK_MAP.get(candlestick):
        raise InvalidCandlestickType(f"Candlestick type {candlestick} is Invalid")

    return CANDLESTICK_MAP[candlestick]()
