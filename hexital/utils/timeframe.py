from datetime import datetime, timedelta
from enum import Enum
from typing import Optional

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


def timeframe_validation(timeframe: Optional[str | TimeFrame | timedelta | int] = None) -> bool:
    if isinstance(timeframe, str):
        timeframe_ = timeframe.upper()
        if isinstance(timeframe_[0], str) and timeframe_[0] in VALID_TIMEFRAME_PREFIXES:
            if len(timeframe_) == 1:
                return True
            elif timeframe_[1].isdigit():
                return True
    elif isinstance(timeframe, (int, timedelta, TimeFrame)):
        return True

    return False


def convert_timeframe_to_timedelta(
    timeframe: Optional[str | TimeFrame | timedelta | int] = None,
) -> timedelta | None:
    if isinstance(timeframe, (str, TimeFrame)):
        return timeframe_to_timedelta(validate_timeframe(timeframe))
    elif isinstance(timeframe, int):
        return timedelta(seconds=timeframe)
    elif isinstance(timeframe, timedelta):
        return timeframe

    return None


def timeframe_to_timedelta(timeframe: str | TimeFrame) -> timedelta:
    # https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases

    timeframe_ = timeframe.value if isinstance(timeframe, TimeFrame) else timeframe.upper()

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
    # https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases
    if not timeframe:
        return ""

    if timeframe < timedelta(seconds=60):
        return f"S{timeframe.seconds}"
    elif (
        timeframe < timedelta(minutes=60)
        or (timeframe < timedelta(hours=24) and timeframe.seconds / 60) % 60 != 0
    ):
        return f"T{int(timeframe.seconds / 60)}"
    elif (
        timeframe < timedelta(hours=24)
        or (timeframe >= timedelta(days=1) and timeframe.total_seconds() / 60 / 60) % 24 != 0
    ):
        return f"H{int(timeframe.total_seconds() / 60 / 60)}"
    elif timeframe >= timedelta(days=1):
        return f"D{int(timeframe.days)}"

    return ""


def validate_timeframe(timeframe: str | TimeFrame) -> str:
    if isinstance(timeframe, str):
        timeframe = timeframe.upper()
        if not isinstance(timeframe[0], str) or timeframe[0] not in VALID_TIMEFRAME_PREFIXES:
            raise InvalidTimeFrame(
                f"Invalid value: {timeframe}, valid are: {VALID_TIMEFRAME_PREFIXES}, E.G 'T10' 10 minutes"
            )
    elif isinstance(timeframe, TimeFrame):
        timeframe = timeframe.value

    return timeframe


def round_down_timestamp(timestamp: datetime, timeframe: timedelta) -> datetime:
    """Find and round down timestamp to the nearest matching timeframe. E.G timeframe of 5 minute
    E.G T5: 09:00:01 -> 9:00:00
    E.G T5: 09:01:20 -> 9:00:00
    E.G T5: 09:05:00 -> 9:05:00
    Note: This method also calls clean_timestamp, removing microseconds
    """
    timestamp = clean_timestamp(timestamp)
    if timeframe < timedelta(days=1):
        return datetime.fromtimestamp(
            timestamp.timestamp() // timeframe.total_seconds() * timeframe.total_seconds()
        )
    elif timeframe < timedelta(days=7):
        return timestamp.replace(hour=0, minute=0, second=0)
    else:
        return timestamp.replace(day=0, hour=0, minute=0, second=0)


def within_timeframe(timestamp: datetime, within: datetime, timeframe: timedelta | None) -> bool:
    """Checks if timestamp is within other timestamp and timeframe period"""
    if not timeframe:
        return False
    return within - timeframe < timestamp <= within


def on_timeframe(timestamp: datetime, timeframe: timedelta) -> bool:
    """Checks if timestamp is on a timeframe value"""
    return timestamp.timestamp() % timeframe.total_seconds() == 0


def clean_timestamp(timestamp: datetime) -> datetime:
    """Removes Microseconds from the timestamp and returns it"""
    return timestamp.replace(microsecond=0)
