from datetime import datetime

import pytest
from hexital import Candle


@pytest.fixture(name="simple_candle_positive")
def fixture_simple_candle_positive():
    return Candle(100, 120, 70, 110, 1)


@pytest.fixture(name="simple_candle")
def fixture_simple_candle():
    return Candle(100, 120, 70, 90, 1)


class TestCoreCandle:
    def test_positive(self, simple_candle_positive):
        assert simple_candle_positive.positive()

    def test_negative(self, simple_candle_positive):
        assert simple_candle_positive.negative() is False

    def test_realbody(self, simple_candle_positive):
        assert simple_candle_positive.realbody() == 10

    def test_shadow_upper(self, simple_candle_positive):
        assert simple_candle_positive.shadow_upper() == 10

    def test_shadow_upper_negative(self, simple_candle):
        assert simple_candle.shadow_upper() == 20

    def test_shadow_lower(self, simple_candle_positive):
        assert simple_candle_positive.shadow_lower() == 30

    def test_shadow_lower_negative(self, simple_candle):
        assert simple_candle.shadow_lower() == 20

    def test_high_low(self, simple_candle):
        assert simple_candle.high_low() == 50


@pytest.fixture(name="candle_dict")
def fixture_candle_dict():
    return [
        {
            "open": 12331.69043,
            "high": 12542.540039,
            "low": 12202.410156,
            "close": 12536.019531,
            "volume": 4918240000,
        },
        {
            "open": 12511.459961,
            "high": 12645.830078,
            "low": 12460.990234,
            "close": 12563.759766,
            "volume": 4547280000,
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


@pytest.fixture(name="candle_list")
def fixture_candle_list():
    return [
        [12331.69043, 12542.540039, 12202.410156, 12536.019531, 4918240000],
        [12511.459961, 12645.830078, 12460.990234, 12563.759766, 4547280000],
    ]


@pytest.fixture(name="candle_list_datetime")
def fixture_candle_list_datetime():
    return [
        12331.69043,
        12542.540039,
        12202.410156,
        12536.019531,
        4918240000,
        datetime(2023, 8, 30),
    ]


def test_candle_from_dict(candle_dict):
    assert Candle.from_dict(candle_dict[0]) == Candle(
        open=12331.69043,
        high=12542.540039,
        low=12202.410156,
        close=12536.019531,
        volume=4918240000,
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


def test_candle_from_dicts(candle_dict):
    assert Candle.from_dicts(candle_dict) == [
        Candle(
            open=12331.69043,
            high=12542.540039,
            low=12202.410156,
            close=12536.019531,
            volume=4918240000,
        ),
        Candle(
            open=12511.459961,
            high=12645.830078,
            low=12460.990234,
            close=12563.759766,
            volume=4547280000,
        ),
    ]


def test_candle_from_list(candle_list):
    assert Candle.from_list(candle_list[0]) == Candle(
        open=12331.69043,
        high=12542.540039,
        low=12202.410156,
        close=12536.019531,
        volume=4918240000,
    )


def test_candle_from_list_datetime(candle_list_datetime):
    assert Candle.from_list(candle_list_datetime) == Candle(
        open=12331.69043,
        high=12542.540039,
        low=12202.410156,
        close=12536.019531,
        volume=4918240000,
        timestamp=datetime(2023, 8, 30),
    )


def test_candle_from_lists(candle_list):
    assert Candle.from_lists(candle_list) == [
        Candle(
            open=12331.69043,
            high=12542.540039,
            low=12202.410156,
            close=12536.019531,
            volume=4918240000,
        ),
        Candle(
            open=12511.459961,
            high=12645.830078,
            low=12460.990234,
            close=12563.759766,
            volume=4547280000,
        ),
    ]
