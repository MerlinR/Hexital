from ..core.candlestick_type import CandlestickType
from ..exceptions import InvalidCandlestickType


def build_candlesticktype(candlestick: CandlestickType | str) -> CandlestickType:
    if isinstance(candlestick, CandlestickType):
        return candlestick

    from ..plugin_manager import plugin_manager

    candlestick_class = plugin_manager.get_candlestick_class(candlestick)

    if not candlestick_class:
        raise InvalidCandlestickType(f"Candlestick type {candlestick} is Invalid")

    return candlestick_class()
