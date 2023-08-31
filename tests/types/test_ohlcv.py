from datetime import datetime

import pytest
from hexital.types import OHLCV


@pytest.fixture(name="ohlcv_dict")
def fixture_ohlcv_dict():
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


@pytest.fixture(name="ohlcv_dict_datetime")
def fixture_ohlcv_dict_datetime():
    return {
        "open": 12331.69043,
        "high": 12542.540039,
        "low": 12202.410156,
        "close": 12536.019531,
        "volume": 4918240000,
        "timestamp": datetime(2023, 8, 30),
    }


@pytest.fixture(name="ohlcv_list")
def fixture_ohlcv_list():
    return [
        [12331.69043, 12542.540039, 12202.410156, 12536.019531, 4918240000],
        [12511.459961, 12645.830078, 12460.990234, 12563.759766, 4547280000],
    ]


@pytest.fixture(name="ohlcv_list_datetime")
def fixture_ohlcv_list_datetime():
    return [
        12331.69043,
        12542.540039,
        12202.410156,
        12536.019531,
        4918240000,
        datetime(2023, 8, 30),
    ]


def test_OHLCV_from_dict(ohlcv_dict):
    assert OHLCV.from_dict(ohlcv_dict[0]) == OHLCV(
        open=12331.69043,
        high=12542.540039,
        low=12202.410156,
        close=12536.019531,
        volume=4918240000,
        indicators={},
        sub_indicators={},
    )


def test_OHLCV_from_dict_datetime(ohlcv_dict_datetime):
    assert OHLCV.from_dict(ohlcv_dict_datetime) == OHLCV(
        open=12331.69043,
        high=12542.540039,
        low=12202.410156,
        close=12536.019531,
        volume=4918240000,
        indicators={},
        sub_indicators={},
        timestamp=datetime(2023, 8, 30),
    )


def test_OHLCV_from_dicts(ohlcv_dict):
    assert OHLCV.from_dicts(ohlcv_dict) == [
        OHLCV(
            open=12331.69043,
            high=12542.540039,
            low=12202.410156,
            close=12536.019531,
            volume=4918240000,
            indicators={},
            sub_indicators={},
        ),
        OHLCV(
            open=12511.459961,
            high=12645.830078,
            low=12460.990234,
            close=12563.759766,
            volume=4547280000,
            indicators={},
            sub_indicators={},
        ),
    ]


def test_OHLCV_from_list(ohlcv_list):
    assert OHLCV.from_list(ohlcv_list[0]) == OHLCV(
        open=12331.69043,
        high=12542.540039,
        low=12202.410156,
        close=12536.019531,
        volume=4918240000,
        indicators={},
        sub_indicators={},
    )


def test_OHLCV_from_list_datetime(ohlcv_list_datetime):
    assert OHLCV.from_list(ohlcv_list_datetime) == OHLCV(
        open=12331.69043,
        high=12542.540039,
        low=12202.410156,
        close=12536.019531,
        volume=4918240000,
        indicators={},
        sub_indicators={},
        timestamp=datetime(2023, 8, 30),
    )


def test_OHLCV_from_lists(ohlcv_list):
    assert OHLCV.from_lists(ohlcv_list) == [
        OHLCV(
            open=12331.69043,
            high=12542.540039,
            low=12202.410156,
            close=12536.019531,
            volume=4918240000,
            indicators={},
            sub_indicators={},
        ),
        OHLCV(
            open=12511.459961,
            high=12645.830078,
            low=12460.990234,
            close=12563.759766,
            volume=4547280000,
            indicators={},
            sub_indicators={},
        ),
    ]
