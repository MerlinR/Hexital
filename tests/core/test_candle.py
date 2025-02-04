from datetime import datetime, timedelta

import pytest
from hexital import Candle


@pytest.fixture(name="simple_candle_positive")
def fixture_simple_candle_positive():
    return Candle(100, 120, 70, 110, 1)


@pytest.fixture(name="simple_candle")
def fixture_simple_candle():
    return Candle(100, 120, 70, 90, 1)


@pytest.fixture(name="merge_candles")
def fixture_simple_candle_merge():
    return [
        Candle(
            open=12331.69,
            high=12542.540,
            low=12202.410,
            close=12536.019,
            volume=500,
            timestamp=datetime(2023, 10, 3, 9, 0, 30),
        ),
        Candle(
            open=12500.69,
            high=12542.540,
            low=11202.410,
            close=11536.019,
            volume=600,
            timestamp=datetime(2023, 10, 3, 9, 1),
        ),
    ]


class TestCoreCandle:
    def test_positive(self, simple_candle_positive):
        assert simple_candle_positive.positive

    def test_negative(self, simple_candle_positive):
        assert simple_candle_positive.negative is False

    def test_realbody(self, simple_candle_positive):
        assert simple_candle_positive.realbody == 10

    def test_shadow_upper(self, simple_candle_positive):
        assert simple_candle_positive.shadow_upper == 10

    def test_shadow_upper_negative(self, simple_candle):
        assert simple_candle.shadow_upper == 20

    def test_shadow_lower(self, simple_candle_positive):
        assert simple_candle_positive.shadow_lower == 30

    def test_shadow_lower_negative(self, simple_candle):
        assert simple_candle.shadow_lower == 20

    def test_high_low(self, simple_candle):
        assert simple_candle.high_low == 50


@pytest.fixture(name="candle_dict")
def fixture_candle_dict():
    return [
        {
            "open": 12331.69043,
            "high": 12542.540039,
            "low": 12202.410156,
            "close": 12536.019531,
            "volume": 4918240000,
            "timestamp": datetime(2023, 8, 30),
        },
        {
            "open": 12511.459961,
            "high": 12645.830078,
            "low": 12460.990234,
            "close": 12563.759766,
            "volume": 4547280000,
            "timestamp": datetime(2023, 8, 30),
        },
    ]


@pytest.fixture(name="candle_dict_datetime")
def fixture_candle_dict_datetime():
    return {
        "open": 12331.69043,
        "high": 12542.540039,
        "low": 12202.410156,
        "close": 12536.019531,
        "volume": 4918240000,
        "timestamp": datetime(2023, 8, 30),
    }


@pytest.fixture(name="candle_dict_timeframe")
def fixture_candle_dict_timeframe():
    return {
        "open": 12331.69043,
        "high": 12542.540039,
        "low": 12202.410156,
        "close": 12536.019531,
        "volume": 4918240000,
        "timestamp": datetime(2023, 8, 30),
        "timeframe": timedelta(minutes=5),
    }


@pytest.fixture(name="candle_dicts_numpy")
def fixture_candle_dicts_numpy():
    # dicts = df.to_dict("records")
    return [
        {
            "open": 14851.6,
            "high": 14854.1,
            "low": 14847.2,
            "close": 14848.1,
            "volume": 247,
            "timestamp": "2023-10-03T09:01:00",
        },
        {
            "open": 14848.2,
            "high": 14848.2,
            "low": 14843.6,
            "close": 14844.7,
            "volume": 332,
            "timestamp": "2023-10-03T09:02:00",
        },
        {
            "open": 14844.6,
            "high": 14846.6,
            "low": 14842.4,
            "close": 14842.6,
            "volume": 196,
            "timestamp": "2023-10-03T09:03:00",
        },
        {
            "open": 14842.5,
            "high": 14842.9,
            "low": 14831.7,
            "close": 14835.6,
            "volume": 540,
            "timestamp": "2023-10-03T09:04:00",
        },
        {
            "open": 14835.5,
            "high": 14842.1,
            "low": 14835.4,
            "close": 14839.7,
            "volume": 171,
            "timestamp": "2023-10-03T09:05:00",
        },
    ]


@pytest.fixture(name="candle_list")
def fixture_candle_list():
    return [
        ["2023-10-03T09:00:00", 12331.69043, 12542.540039, 12202.410156, 12536.019531, 4918240000],
        [
            "2023-10-03T09:05:00",
            12511.459961,
            12645.830078,
            12460.990234,
            12563.759766,
            4547280000,
        ],
    ]


@pytest.fixture(name="candle_list_timeframe")
def fixture_candle_list_timeframe():
    return [
        [
            "2023-10-03T09:00:00",
            12331.69043,
            12542.540039,
            12202.410156,
            12536.019531,
            4918240000,
            timedelta(minutes=5),
        ],
        [
            "2023-10-03T09:05:00",
            12511.459961,
            12645.830078,
            12460.990234,
            12563.759766,
            4547280000,
            timedelta(minutes=5),
        ],
    ]


def test_candle_from_dict(candle_dict):
    assert Candle.from_dict(candle_dict[0]) == Candle(
        open=12331.69043,
        high=12542.540039,
        low=12202.410156,
        close=12536.019531,
        volume=4918240000,
        timestamp=datetime(2023, 8, 30),
    )


def test_candle_from_dict_datetime(candle_dict_datetime):
    assert Candle.from_dict(candle_dict_datetime) == Candle(
        open=12331.69043,
        high=12542.540039,
        low=12202.410156,
        close=12536.019531,
        volume=4918240000,
        timestamp=datetime(2023, 8, 30),
    )


def test_candle_from_dict_timeframe(candle_dict_timeframe):
    assert Candle.from_dict(candle_dict_timeframe) == Candle(
        open=12331.69043,
        high=12542.540039,
        low=12202.410156,
        close=12536.019531,
        volume=4918240000,
        timestamp=datetime(2023, 8, 30),
        timeframe="T5",
    )


def test_candle_from_dicts(candle_dict):
    assert Candle.from_dicts(candle_dict) == [
        Candle(
            open=12331.69043,
            high=12542.540039,
            low=12202.410156,
            close=12536.019531,
            volume=4918240000,
            timestamp=datetime(2023, 8, 30),
        ),
        Candle(
            open=12511.459961,
            high=12645.830078,
            low=12460.990234,
            close=12563.759766,
            volume=4547280000,
            timestamp=datetime(2023, 8, 30),
        ),
    ]


def test_candle_from_dicts_numpy(candle_dicts_numpy):
    assert Candle.from_dicts(candle_dicts_numpy) == [
        Candle(
            open=14851.6,
            high=14854.1,
            low=14847.2,
            close=14848.1,
            volume=247,
            timestamp=datetime(2023, 10, 3, 9, 1),
        ),
        Candle(
            open=14848.2,
            high=14848.2,
            low=14843.6,
            close=14844.7,
            volume=332,
            timestamp=datetime(2023, 10, 3, 9, 2),
        ),
        Candle(
            open=14844.6,
            high=14846.6,
            low=14842.4,
            close=14842.6,
            volume=196,
            timestamp=datetime(2023, 10, 3, 9, 3),
        ),
        Candle(
            open=14842.5,
            high=14842.9,
            low=14831.7,
            close=14835.6,
            volume=540,
            timestamp=datetime(2023, 10, 3, 9, 4),
        ),
        Candle(
            open=14835.5,
            high=14842.1,
            low=14835.4,
            close=14839.7,
            volume=171,
            timestamp=datetime(2023, 10, 3, 9, 5),
        ),
    ]


def test_candle_from_list(candle_list):
    assert Candle.from_list(candle_list[0]) == Candle(
        open=12331.69043,
        high=12542.540039,
        low=12202.410156,
        close=12536.019531,
        volume=4918240000,
        timestamp=datetime(2023, 10, 3, 9, 0),
    )


def test_candle_from_list_timeframe(candle_list_timeframe):
    assert Candle.from_list(candle_list_timeframe[0]) == Candle(
        open=12331.69043,
        high=12542.540039,
        low=12202.410156,
        close=12536.019531,
        volume=4918240000,
        timestamp=datetime(2023, 10, 3, 9, 0),
        timeframe=timedelta(minutes=5),
    )


def test_candle_from_lists(candle_list):
    assert Candle.from_lists(candle_list) == [
        Candle(
            open=12331.69043,
            high=12542.540039,
            low=12202.410156,
            close=12536.019531,
            volume=4918240000,
            timestamp=datetime(2023, 10, 3, 9, 0),
        ),
        Candle(
            open=12511.459961,
            high=12645.830078,
            low=12460.990234,
            close=12563.759766,
            volume=4547280000,
            timestamp=datetime(2023, 10, 3, 9, 5),
        ),
    ]


class TestCandleCollapsedTimestamp:
    def test_candle_merge_collapse_timestamp(self, merge_candles):
        main_candle = merge_candles[0]
        main_candle.set_collapsed_timestamp(datetime(2023, 10, 3, 9, 5))

        assert main_candle.timestamp == datetime(2023, 10, 3, 9, 5)
        assert main_candle._start_timestamp == datetime(2023, 10, 3, 9, 0, 30)


class TestCandleMerge:
    def test_candle_merge_basic(self, merge_candles):
        main_candle = merge_candles[0]
        second_candle = merge_candles[1]

        main_candle.merge(second_candle)
        expected = Candle(
            open=12331.69,
            high=12542.540,
            low=11202.410,
            close=11536.019,
            volume=1100,
            timestamp=datetime(2023, 10, 3, 9, 0, 30),
        )
        expected.aggregation_factor = 2
        assert main_candle == expected and main_candle._start_timestamp is None

    def test_candle_merge_basic_collapse(self, merge_candles):
        main_candle = merge_candles[0]
        main_candle.set_collapsed_timestamp(datetime(2023, 10, 3, 9, 5))

        second_candle = merge_candles[1]

        main_candle.merge(second_candle)

        assert main_candle._start_timestamp == datetime(2023, 10, 3, 9, 0, 30)
        assert main_candle._end_timestamp == datetime(2023, 10, 3, 9, 1)

    def test_candle_merge_wrongorder(self, merge_candles):
        main_candle = merge_candles[1]
        main_candle.set_collapsed_timestamp(datetime(2023, 10, 3, 9, 5))

        second_candle = merge_candles[0]

        main_candle.merge(second_candle)

        assert main_candle.timestamp == datetime(2023, 10, 3, 9, 5)
        assert main_candle._start_timestamp == datetime(2023, 10, 3, 9, 0, 30)
        assert main_candle._end_timestamp == datetime(2023, 10, 3, 9, 1)

    def test_candle_merge_out_of_timeframe_over(self, merge_candles):
        main_candle = merge_candles[0]
        second_candle = merge_candles[1]
        main_candle.timeframe = timedelta(minutes=1)
        second_candle.timestamp = datetime(2023, 10, 3, 9, 5)
        main_candle.merge(second_candle)

        assert (
            main_candle.timestamp == datetime(2023, 10, 3, 9, 0, 30)
            and main_candle.close == 12536.019
        )

    def test_candle_merge_out_of_timeframe_under(self, merge_candles):
        main_candle = merge_candles[0]
        second_candle = merge_candles[1]
        main_candle.timeframe = timedelta(minutes=1)
        second_candle.timestamp = datetime(2023, 10, 3, 8, 55)
        main_candle.merge(second_candle)

        assert (
            main_candle.timestamp == datetime(2023, 10, 3, 9, 0, 30)
            and main_candle.close == 12536.019
        )


class TestCandleTo:
    def test_candle_to_list(self):
        candle = Candle(
            12331.69043,
            12542.540039,
            12202.410156,
            12536.019531,
            4918240000,
            datetime(2023, 10, 3, 9),
        )
        expected = [
            datetime(2023, 10, 3, 9),
            12331.69043,
            12542.540039,
            12202.410156,
            12536.019531,
            4918240000,
        ]

        assert candle.as_list() == expected

    def test_candle_to_list_timeframe(self):
        candle = Candle(
            12331.69043,
            12542.540039,
            12202.410156,
            12536.019531,
            4918240000,
            datetime(2023, 10, 3, 9),
            timeframe="H1",
        )
        expected = [
            datetime(2023, 10, 3, 9),
            12331.69043,
            12542.540039,
            12202.410156,
            12536.019531,
            4918240000,
            timedelta(hours=1),
        ]

        assert candle.as_list() == expected

    def test_candle_to_dict(self):
        candle = Candle(
            12331.69043,
            12542.540039,
            12202.410156,
            12536.019531,
            4918240000,
            datetime(2023, 10, 3, 9),
        )

        expected = {
            "open": 12331.69043,
            "high": 12542.540039,
            "low": 12202.410156,
            "close": 12536.019531,
            "volume": 4918240000,
            "timestamp": datetime(2023, 10, 3, 9),
        }
        assert candle.as_dict() == expected

    def test_candle_to_dict_timeframe(self):
        candle = Candle(
            12331.69043,
            12542.540039,
            12202.410156,
            12536.019531,
            4918240000,
            datetime(2023, 10, 3, 9),
            timeframe="H1",
        )

        expected = {
            "open": 12331.69043,
            "high": 12542.540039,
            "low": 12202.410156,
            "close": 12536.019531,
            "volume": 4918240000,
            "timestamp": datetime(2023, 10, 3, 9),
            "timeframe": timedelta(hours=1),
        }
        assert candle.as_dict() == expected
