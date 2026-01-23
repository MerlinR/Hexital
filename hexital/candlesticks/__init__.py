from ..core.candlestick_type import CandlestickType
from .heikinashi import HeikinAshi


def _build_candlestick_map() -> dict[str, type[CandlestickType]]:
    """Auto-discover all CandlestickType subclasses and map by acronym"""
    return {
        cls.acronym: cls
        for cls in CandlestickType.__subclasses__()
        if hasattr(cls, "acronym") and cls.acronym != "NA"
    }


CANDLESTICK_MAP = _build_candlestick_map()

__all__ = ["CANDLESTICK_MAP", "HeikinAshi"]
