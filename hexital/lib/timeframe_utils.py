from datetime import datetime, timedelta

from hexital.exceptions import InvalidTimeFrame

VALID_TIMEFRAME_PREFIXES = ["S", "T", "H", "D"]


def round_down_timestamp(timestamp: datetime, timeframe: timedelta) -> datetime:
    return datetime.fromtimestamp(
        timestamp.timestamp() // timeframe.total_seconds() * timeframe.total_seconds()
    )


def timeframe_to_timedelta(timeframe: str) -> timedelta:
    # https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases
    timeframe = timeframe.upper()
    if not isinstance(timeframe[0], str) or timeframe[0] not in VALID_TIMEFRAME_PREFIXES:
        raise InvalidTimeFrame(
            f"Invalid value: {timeframe}, valid are: {VALID_TIMEFRAME_PREFIXES}"
        )
    if timeframe.startswith("S"):
        return timedelta(seconds=int(timeframe[1:]))
    if timeframe.startswith("T"):
        return timedelta(minutes=int(timeframe[1:]))
    if timeframe.startswith("H"):
        return timedelta(hours=int(timeframe[1:]))
    if timeframe.startswith("D"):
        return timedelta(days=int(timeframe[1:]))

    InvalidTimeFrame(f"Invalid value: {timeframe}, somehow")
