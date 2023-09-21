class InvalidIndicator(Exception):
    def __init__(self, message):
        super().__init__(message)


class InvalidPattern(Exception):
    def __init__(self, message):
        super().__init__(message)


class InvalidTimeFrame(Exception):
    def __init__(self, message):
        super().__init__(message)
