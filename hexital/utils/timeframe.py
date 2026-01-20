from __future__ import annotations

from datetime import datetime, timedelta
from enum import Enum
from typing import TypeAlias

from hexital.exceptions import InvalidTimeFrame

VALID_TIMEFRAME_PREFIXES = ["S", "T", "H", "D"]


class TimeFrame(Enum):
    """Pre-defined TimeFrame values"""

    SECOND = "S1"
    SECOND5 = "S5"
    SECOND10 = "S10"
    SECOND15 = "S15"
    SECOND30 = "S30"
    MINUTE = "T1"
    MINUTE5 = "T5"
    MINUTE10 = "T10"
    MINUTE15 = "T15"
    MINUTE30 = "T30"
    MINUTE45 = "T45"
    HOUR = "H1"
    HOUR2 = "H2"
    HOUR3 = "H3"
    HOUR4 = "H4"
    DAY = "D1"
    WEEK = "D7"


TimeFramesSource: TypeAlias = str | TimeFrame | timedelta | int


def timeframe_validation(timeframe: TimeFramesSource | None = None) -> bool:
    if isinstance(timeframe, (int, timedelta, TimeFrame)):
        return True

    if isinstance(timeframe, str):
        timeframe_ = timeframe.upper()
        if timeframe_[0] in VALID_TIMEFRAME_PREFIXES:
            return len(timeframe_) == 1 or timeframe_[1:].isdigit()

    return False


def convert_timeframe_to_timedelta(
    timeframe: TimeFramesSource | None = None,
) -> timedelta | None:
    if isinstance(timeframe, (str, TimeFrame)):
        return timeframe_to_timedelta(validate_timeframe(timeframe))
    if isinstance(timeframe, int):
        return timedelta(seconds=timeframe)
    if isinstance(timeframe, timedelta):
        return timeframe

    return None


def timeframe_to_timedelta(timeframe: str | TimeFrame) -> timedelta:
    # https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases

    timeframe_ = (
        timeframe.value if isinstance(timeframe, TimeFrame) else timeframe.upper()
    )

    if not timeframe_validation(timeframe_):
        raise InvalidTimeFrame(
            f"Invalid value: {timeframe_}, valid are: {VALID_TIMEFRAME_PREFIXES}, E.G 'T10' 10 minutes"
        )

    letter = timeframe_[0]
    time = 1 if len(timeframe_) == 1 else int(timeframe_[1:])

    if letter == "S":
        return timedelta(seconds=time)
    if letter == "T":
        return timedelta(minutes=time)
    if letter == "H":
        return timedelta(hours=time)
    if letter == "D":
        return timedelta(days=time)

    raise InvalidTimeFrame(f"Invalid value: {timeframe_}, somehow")


def timedelta_to_str(timeframe: timedelta) -> str:
    if not timeframe:
        return ""

    total_seconds = timeframe.total_seconds()

    # Days
    if total_seconds >= 86400 and total_seconds % 86400 == 0:
        return f"D{int(timeframe.days)}"
    # Hours
    if total_seconds >= 3600 and total_seconds % 3600 == 0:
        return f"H{int(total_seconds / 3600)}"
    # Minutes
    if total_seconds >= 60 and total_seconds % 60 == 0:
        return f"T{int(total_seconds / 60)}"
    # Seconds
    return f"S{int(total_seconds)}"


def validate_timeframe(timeframe: str | TimeFrame) -> str:
    if isinstance(timeframe, TimeFrame):
        return timeframe.value

    timeframe = timeframe.upper()
    if timeframe[0] not in VALID_TIMEFRAME_PREFIXES:
        raise InvalidTimeFrame(
            f"Invalid value: {timeframe}, valid are: {VALID_TIMEFRAME_PREFIXES}, E.G 'T10' 10 minutes"
        )

    return timeframe


def round_down_timestamp(timestamp: datetime, timeframe: timedelta) -> datetime:
    """Find and round down timestamp to the nearest matching timeframe. E.G timeframe of 5 minute
    E.G T5: 09:00:01 -> 9:00:00
    E.G T5: 09:01:20 -> 9:00:00
    E.G T5: 09:05:00 -> 9:05:00
    Note: This method also calls trim_timestamp, removing microseconds
    """
    timestamp = timestamp.replace(microsecond=0)

    if timeframe < timedelta(days=1):
        seconds = timeframe.total_seconds()
        rounded_ts = (timestamp.timestamp() // seconds) * seconds
        return datetime.fromtimestamp(rounded_ts, tz=timestamp.tzinfo)

    if timeframe >= timedelta(days=7):
        days_since_monday = timestamp.isoweekday() - 1
        return (timestamp - timedelta(days=days_since_monday)).replace(
            hour=0, minute=0, second=0
        )

    return timestamp.replace(hour=0, minute=0, second=0)


def within_timeframe(
    timestamp: datetime, within: datetime, timeframe: timedelta | None
) -> bool:
    """Checks if timestamp is within other timestamp and timeframe period"""
    if not timeframe:
        return False
    return within - timeframe < timestamp <= within


def on_timeframe(timestamp: datetime, timeframe: timedelta) -> bool:
    """Checks if timestamp is on a timeframe value"""
    return timestamp.timestamp() % timeframe.total_seconds() == 0
