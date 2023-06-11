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
