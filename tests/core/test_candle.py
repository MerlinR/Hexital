from datetime import datetime

import pytest
from hexital.core import Candle


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
        indicators={},
        sub_indicators={},
    )


def test_candle_from_dict_datetime(candle_dict_datetime):
    assert Candle.from_dict(candle_dict_datetime) == Candle(
        open=12331.69043,
        high=12542.540039,
        low=12202.410156,
        close=12536.019531,
        volume=4918240000,
        indicators={},
        sub_indicators={},
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
            indicators={},
            sub_indicators={},
        ),
        Candle(
            open=12511.459961,
            high=12645.830078,
            low=12460.990234,
            close=12563.759766,
            volume=4547280000,
            indicators={},
            sub_indicators={},
        ),
    ]


def test_candle_from_list(candle_list):
    assert Candle.from_list(candle_list[0]) == Candle(
        open=12331.69043,
        high=12542.540039,
        low=12202.410156,
        close=12536.019531,
        volume=4918240000,
        indicators={},
        sub_indicators={},
    )


def test_candle_from_list_datetime(candle_list_datetime):
    assert Candle.from_list(candle_list_datetime) == Candle(
        open=12331.69043,
        high=12542.540039,
        low=12202.410156,
        close=12536.019531,
        volume=4918240000,
        indicators={},
        sub_indicators={},
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
            indicators={},
            sub_indicators={},
        ),
        Candle(
            open=12511.459961,
            high=12645.830078,
            low=12460.990234,
            close=12563.759766,
            volume=4547280000,
            indicators={},
            sub_indicators={},
        ),
    ]
