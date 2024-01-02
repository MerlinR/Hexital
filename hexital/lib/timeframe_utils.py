from datetime import datetime, timedelta

from hexital.exceptions import InvalidTimeFrame

VALID_TIMEFRAME_PREFIXES = ["S", "T", "H", "D"]


def round_down_timestamp(timestamp: datetime, timeframe: timedelta) -> datetime:
    """Find and round down timestamp to the nearest matching timeframe. E.G timeframe of 5 minute
    E.G T5: 09:00:01 -> 9:00:00
    E.G T5: 09:01:20 -> 9:00:00
    E.G T5: 09:05:00 -> 9:05:00
    Note: This method also calls clean_timestamp, removing microseconds
    """
    timestamp = clean_timestamp(timestamp)
    return datetime.fromtimestamp(
        timestamp.timestamp() // timeframe.total_seconds() * timeframe.total_seconds()
    )


def on_timeframe(timestamp: datetime, timeframe: timedelta) -> bool:
    """Checks if timestamp is on a timeframe value"""
    return timestamp.timestamp() % timeframe.total_seconds() == 0


def clean_timestamp(timestamp: datetime) -> datetime:
    """Removes Microseconds from the timestamp and returns it"""
    return timestamp.replace(microsecond=0)


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

    raise InvalidTimeFrame(f"Invalid value: {timeframe}, somehow")
