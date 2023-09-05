import pytest
from hexital.types.ohlcv import OHLCV
from hexital.utilities import patterns


@pytest.fixture(name="doji_candle")
def fixture_doji_candle():
    return [
        OHLCV(open=15344.3, high=15345.8, low=15339.9, close=15341.3, volume=154),
        OHLCV(open=15341.4, high=15345.3, low=15340.8, close=15343.1, volume=195),
        OHLCV(open=15343.4, high=15345.1, low=15342.1, close=15344.4, volume=129),
        OHLCV(open=15344.5, high=15345.9, low=15340.9, close=15341.3, volume=81),
        OHLCV(open=15341, high=15341, low=15337.4, close=15337.4, volume=149),
        OHLCV(open=15337.5, high=15340.4, low=15337.5, close=15338.1, volume=82),
        OHLCV(open=15338.3, high=15340.4, low=15336.9, close=15340.1, volume=103),
        OHLCV(open=15340, high=15342.4, low=15339.6, close=15340.9, volume=71),
        OHLCV(open=15340.8, high=15340.9, low=15336, close=15339.1, volume=107),
        OHLCV(open=15339, high=15340.5, low=15338, close=15338.6, volume=65),
        OHLCV(open=15339.9, high=15340.1, low=15336.8, close=15339.9, volume=82),
        OHLCV(open=15340, high=15345, low=15338.1, close=15343.6, volume=126),
    ]


def test_doji_candle(doji_candle):
    assert patterns.doji(doji_candle) is False


def test_doji_candle_lookback(doji_candle):
    assert patterns.doji(doji_candle, lookback=2) is True
