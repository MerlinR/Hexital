class InvalidIndicator(Exception):
    pass


class InvalidIndicatorParameter(Exception):
    pass


class InvalidAnalysis(Exception):
    pass


class InvalidTimeFrame(Exception):
    pass


class InvalidCandleOrder(Exception):
    pass


class InvalidCandlestickType(Exception):
    pass


class InvalidConfiguration(Exception):
    pass


__all__ = [
    "InvalidAnalysis",
    "InvalidCandleOrder",
    "InvalidCandlestickType",
    "InvalidConfiguration",
    "InvalidIndicator",
    "InvalidIndicatorParameter",
    "InvalidTimeFrame",
]
