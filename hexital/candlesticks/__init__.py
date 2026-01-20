from .heikinashi import HeikinAshi

CANDLESTICK_MAP = {
    "HA": HeikinAshi,
}

__all__ = ["CANDLESTICK_MAP", "HeikinAshi"]
