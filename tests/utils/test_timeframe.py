from datetime import datetime, timedelta

import pytest
from hexital import TimeFrame
from hexital.exceptions import InvalidTimeFrame
from hexital.utils.timeframe import (
    round_down_timestamp,
    timedelta_to_str,
    timeframe_to_timedelta,
    within_timeframe,
)


class TestRoundDownTimestamp:
    def test_round_down_minutes_no_change(self):
        assert round_down_timestamp(
            datetime(2023, 6, 6, 12, 0, 0), timedelta(minutes=1)
        ) == datetime(2023, 6, 6, 12, 0, 0)

    def test_round_down_minutes_remove_seconds_and_mili(self):
        assert round_down_timestamp(
            datetime(2023, 6, 6, 12, 0, 43, 3857), timedelta(minutes=1)
        ) == datetime(2023, 6, 6, 12, 0, 0)

    def test_round_down_t10_minutes(self):
        assert round_down_timestamp(
            datetime(2023, 6, 6, 12, 9, 43, 3857), timedelta(minutes=10)
        ) == datetime(2023, 6, 6, 12, 0, 0)

    def test_round_down_t10_minutes_two(self):
        assert round_down_timestamp(
            datetime(2023, 6, 6, 12, 19, 43, 3857), timedelta(minutes=10)
        ) == datetime(2023, 6, 6, 12, 10, 0)

    def test_round_down_h1(self):
        assert round_down_timestamp(
            datetime(2023, 6, 6, 12, 9, 43, 3857), timedelta(hours=1)
        ) == datetime(2023, 6, 6, 12, 0, 0)

    def test_round_down_h1_same(self):
        assert round_down_timestamp(
            datetime(2023, 6, 6, 12, 0, 0, 0), timedelta(hours=1)
        ) == datetime(2023, 6, 6, 12, 0, 0)

    def test_round_down_d1(self):
        assert round_down_timestamp(
            datetime(2023, 6, 6, 12, 9, 43, 3857), timedelta(days=1)
        ) == datetime(2023, 6, 6, 0, 0, 0)


class TestTimeframeToTimeDelta:
    def test_timeframe_to_delta_min(self):
        assert timeframe_to_timedelta("T10") == timedelta(minutes=10)

    def test_timeframe_to_delta_secs(self):
        assert timeframe_to_timedelta("S10") == timedelta(seconds=10)

    def test_timeframe_to_delta_secs_long(self):
        assert timeframe_to_timedelta("S90") == timedelta(minutes=1, seconds=30)

    def test_timeframe_to_delta_hours(self):
        assert timeframe_to_timedelta("H5") == timedelta(hours=5)

    def test_timeframe_to_delta_days(self):
        assert timeframe_to_timedelta("D1") == timedelta(days=1)

    def test_timeframe_to_delta_invalid_key(self):
        with pytest.raises(InvalidTimeFrame):
            assert timeframe_to_timedelta("u30")

    def test_timeframe_to_delta_no_key(self):
        with pytest.raises(InvalidTimeFrame):
            assert timeframe_to_timedelta("30")

    def test_timeframe_enum_to_delta_min(self):
        assert timeframe_to_timedelta(TimeFrame.MINUTE10) == timedelta(minutes=10)

    def test_timeframe_enum_to_delta_secs(self):
        assert timeframe_to_timedelta(TimeFrame.SECOND10) == timedelta(seconds=10)


class TestTimedeltaToStr:
    def test_timedelta_to_str_seconds(self):
        assert timedelta_to_str(timedelta(seconds=30)) == "S30"

    def test_timedelta_to_str_minutes(self):
        assert timedelta_to_str(timedelta(minutes=1)) == "T1"

    def test_timedelta_to_str_minutes_two(self):
        assert timedelta_to_str(timedelta(minutes=5)) == "T5"

    def test_timedelta_to_str_minutes_three(self):
        assert timedelta_to_str(timedelta(minutes=30)) == "T30"

    def test_timedelta_to_str_minutes_long(self):
        assert timedelta_to_str(timedelta(minutes=90)) == "T90"

    def test_timedelta_to_str_hours(self):
        assert timedelta_to_str(timedelta(hours=1)) == "H1"

    def test_timedelta_to_str_hours_two(self):
        assert timedelta_to_str(timedelta(hours=6)) == "H6"

    def test_timedelta_to_str_hours_long(self):
        assert timedelta_to_str(timedelta(hours=36)) == "H36"

    def test_timedelta_to_str_days(self):
        assert timedelta_to_str(timedelta(days=6)) == "D6"


class TestWithinTimeframe:
    def test_within_basic(self):
        assert within_timeframe(
            datetime(2024, 6, 9, 9, 3, 0), datetime(2024, 6, 9, 9, 5, 0), timedelta(minutes=5)
        )

    def test_within_false(self):
        assert not within_timeframe(
            datetime(2024, 6, 9, 9, 7, 0), datetime(2024, 6, 9, 9, 5, 0), timedelta(minutes=5)
        )

    def test_within_on(self):
        assert within_timeframe(
            datetime(2024, 6, 9, 9, 5, 0), datetime(2024, 6, 9, 9, 5, 0), timedelta(minutes=5)
        )
