from datetime import datetime, timedelta
from enum import Enum

from hexital.exceptions import InvalidTimeFrame

VALID_TIMEFRAME_PREFIXES = ["S", "T", "H", "D"]


class TimeFrame(Enum):
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
    return datetime.fromtimestamp(
        timestamp.timestamp() // timeframe.total_seconds() * timeframe.total_seconds()
    )


def on_timeframe(timestamp: datetime, timeframe: timedelta) -> bool:
    """Checks if timestamp is on a timeframe value"""
    return timestamp.timestamp() % timeframe.total_seconds() == 0


def clean_timestamp(timestamp: datetime) -> datetime:
    """Removes Microseconds from the timestamp and returns it"""
    return timestamp.replace(microsecond=0)


def timeframe_to_timedelta(timeframe: str | TimeFrame) -> timedelta:
    # https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases

    timeframe_ = timeframe.value if isinstance(timeframe, TimeFrame) else timeframe.upper()

    if not isinstance(timeframe_[0], str) or timeframe_[0] not in VALID_TIMEFRAME_PREFIXES:
        raise InvalidTimeFrame(
            f"Invalid value: {timeframe_}, valid are: {VALID_TIMEFRAME_PREFIXES}, E.G 'T10' 10 minutes"
        )

    if timeframe_.startswith("S"):
        return timedelta(seconds=int(timeframe_[1:]))
    if timeframe_.startswith("T"):
        return timedelta(minutes=int(timeframe_[1:]))
    if timeframe_.startswith("H"):
        return timedelta(hours=int(timeframe_[1:]))
    if timeframe_.startswith("D"):
        return timedelta(days=int(timeframe_[1:]))

    raise InvalidTimeFrame(f"Invalid value: {timeframe_}, somehow")
