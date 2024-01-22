class InvalidIndicator(Exception):
    def __init__(self, message):
        super().__init__(message)


class InvalidAnalysis(Exception):
    def __init__(self, message):
        super().__init__(message)


class InvalidTimeFrame(Exception):
    def __init__(self, message):
        super().__init__(message)


class InvalidCandleOrder(Exception):
    def __init__(self, message):
        super().__init__(message)
