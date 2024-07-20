from datetime import datetime, timedelta

import pytest
from hexital import TimeFrame
from hexital.exceptions import InvalidTimeFrame
from hexital.utils.timeframe import (
    round_down_timestamp,
    timedelta_to_str,
    timeframe_to_timedelta,
)


def test_timeframe_to_delta_min():
    assert timeframe_to_timedelta("T10") == timedelta(minutes=10)


def test_timeframe_to_delta_secs():
    assert timeframe_to_timedelta("S10") == timedelta(seconds=10)


def test_timeframe_to_delta_secs_long():
    assert timeframe_to_timedelta("S90") == timedelta(minutes=1, seconds=30)


def test_timeframe_to_delta_hours():
    assert timeframe_to_timedelta("H5") == timedelta(hours=5)


def test_timeframe_to_delta_days():
    assert timeframe_to_timedelta("D1") == timedelta(days=1)


def test_timeframe_to_delta_invalid_key():
    with pytest.raises(InvalidTimeFrame):
        assert timeframe_to_timedelta("u30")


def test_timeframe_to_delta_no_key():
    with pytest.raises(InvalidTimeFrame):
        assert timeframe_to_timedelta("30")


def test_timeframe_enum_to_delta_min():
    assert timeframe_to_timedelta(TimeFrame.MINUTE10) == timedelta(minutes=10)


def test_timeframe_enum_to_delta_secs():
    assert timeframe_to_timedelta(TimeFrame.SECOND10) == timedelta(seconds=10)


def test_round_down_minutes_no_change():
    assert round_down_timestamp(datetime(2023, 6, 6, 12, 0, 0), timedelta(minutes=1)) == datetime(
        2023, 6, 6, 12, 0, 0
    )


def test_round_down_minutes_remove_seconds_and_mili():
    assert round_down_timestamp(
        datetime(2023, 6, 6, 12, 0, 43, 3857), timedelta(minutes=1)
    ) == datetime(2023, 6, 6, 12, 0, 0)


def test_round_down_t10_minutes():
    assert round_down_timestamp(
        datetime(2023, 6, 6, 12, 9, 43, 3857), timedelta(minutes=10)
    ) == datetime(2023, 6, 6, 12, 0, 0)


def test_round_down_t10_minutes_two():
    assert round_down_timestamp(
        datetime(2023, 6, 6, 12, 19, 43, 3857), timedelta(minutes=10)
    ) == datetime(2023, 6, 6, 12, 10, 0)


def test_round_down_h1():
    assert round_down_timestamp(
        datetime(2023, 6, 6, 12, 9, 43, 3857), timedelta(hours=1)
    ) == datetime(2023, 6, 6, 12, 0, 0)


def test_round_down_h1_same():
    assert round_down_timestamp(datetime(2023, 6, 6, 12, 0, 0, 0), timedelta(hours=1)) == datetime(
        2023, 6, 6, 12, 0, 0
    )


def test_round_down_d1():
    assert round_down_timestamp(
        datetime(2023, 6, 6, 12, 9, 43, 3857), timedelta(days=1)
    ) == datetime(2023, 6, 6, 0, 0, 0)


def test_timedelta_to_str_seconds():
    assert timedelta_to_str(timedelta(seconds=30)) == "S30"


def test_timedelta_to_str_minutes():
    assert timedelta_to_str(timedelta(minutes=1)) == "T1"


def test_timedelta_to_str_minutes_two():
    assert timedelta_to_str(timedelta(minutes=5)) == "T5"


def test_timedelta_to_str_minutes_three():
    assert timedelta_to_str(timedelta(minutes=30)) == "T30"


def test_timedelta_to_str_minutes_long():
    assert timedelta_to_str(timedelta(minutes=90)) == "T90"


def test_timedelta_to_str_hours():
    assert timedelta_to_str(timedelta(hours=1)) == "H1"


def test_timedelta_to_str_hours_two():
    assert timedelta_to_str(timedelta(hours=6)) == "H6"


def test_timedelta_to_str_hours_long():
    assert timedelta_to_str(timedelta(hours=36)) == "H36"


def test_timedelta_to_str_days():
    assert timedelta_to_str(timedelta(days=6)) == "D6"
