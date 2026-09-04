import pytest
from hexital.analysis import patterns
from hexital.core.candle import Candle


@pytest.fixture(name="doji_candle")
def fixture_doji_candle():
    return [
        Candle(open=15344.3, high=15345.8, low=15339.9, close=15341.3, volume=154),
        Candle(open=15341.4, high=15345.3, low=15340.8, close=15343.1, volume=195),
        Candle(open=15343.4, high=15345.1, low=15342.1, close=15344.4, volume=129),
        Candle(open=15344.5, high=15345.9, low=15340.9, close=15341.3, volume=81),
        Candle(open=15341, high=15341, low=15337.4, close=15337.4, volume=149),
        Candle(open=15337.5, high=15340.4, low=15337.5, close=15338.1, volume=82),
        Candle(open=15338.3, high=15340.4, low=15336.9, close=15340.1, volume=103),
        Candle(open=15340, high=15342.4, low=15339.6, close=15340.9, volume=71),
        Candle(open=15340.8, high=15340.9, low=15336, close=15339.1, volume=107),
        Candle(open=15339, high=15340.5, low=15338, close=15338.6, volume=65),
        Candle(open=15339.9, high=15340.1, low=15336.8, close=15339.9, volume=82),
        Candle(open=15340, high=15345, low=15338.1, close=15343.6, volume=126),
    ]


def test_doji_candle(doji_candle):
    assert patterns.doji(doji_candle) is False


def test_doji_candle_lookback(doji_candle):
    assert patterns.doji(doji_candle, lookback=2) is True


def test_doji_lookback_honours_index():
    from datetime import datetime, timedelta

    base = datetime(2026, 1, 1)
    candles = []
    for index in range(20):
        if index == 18:
            candles.append(
                Candle(
                    open=100,
                    high=100.4,
                    low=99.6,
                    close=100.01,
                    volume=1,
                    timestamp=base + timedelta(minutes=index),
                )
            )
        else:
            candles.append(
                Candle(
                    open=100,
                    high=120,
                    low=80,
                    close=110,
                    volume=1,
                    timestamp=base + timedelta(minutes=index),
                )
            )

    assert patterns.doji(candles, index=18) is True
    assert patterns.doji(candles, lookback=3, index=5) is False
    assert patterns.doji(candles, lookback=3, index=18) is True


@pytest.fixture(name="bullish_engulfing_candles")
def fixture_bullish_engulfing_candles():
    return [
        Candle(open=100, high=105, low=95, close=102, volume=1),
        Candle(open=110, high=112, low=98, close=100, volume=1),
        Candle(open=99, high=115, low=98, close=111, volume=1),
    ]


@pytest.fixture(name="bearish_engulfing_candles")
def fixture_bearish_engulfing_candles():
    return [
        Candle(open=100, high=105, low=95, close=98, volume=1),
        Candle(open=100, high=112, low=99, close=110, volume=1),
        Candle(open=111, high=113, low=89, close=90, volume=1),
    ]


def test_bullish_engulfing(bullish_engulfing_candles):
    assert patterns.bullish_engulfing(bullish_engulfing_candles, index=0) is False
    assert patterns.bullish_engulfing(bullish_engulfing_candles, index=1) is False
    assert patterns.bullish_engulfing(bullish_engulfing_candles, index=2) is True
    assert patterns.bearish_engulfing(bullish_engulfing_candles, index=2) is False


def test_bullish_engulfing_lookback(bullish_engulfing_candles):
    assert patterns.bullish_engulfing(bullish_engulfing_candles, lookback=2) is True
    assert patterns.bullish_engulfing(bullish_engulfing_candles, lookback=1) is True


def test_bearish_engulfing(bearish_engulfing_candles):
    assert patterns.bearish_engulfing(bearish_engulfing_candles, index=0) is False
    assert patterns.bearish_engulfing(bearish_engulfing_candles, index=1) is False
    assert patterns.bearish_engulfing(bearish_engulfing_candles, index=2) is True
    assert patterns.bullish_engulfing(bearish_engulfing_candles, index=2) is False


def test_bearish_engulfing_lookback(bearish_engulfing_candles):
    assert patterns.bearish_engulfing(bearish_engulfing_candles, lookback=2) is True


def test_engulfing_requires_larger_body():
    candles = [
        Candle(open=110, high=112, low=98, close=100, volume=1),
        Candle(open=100, high=105, low=99, close=104, volume=1),
    ]
    assert patterns.bullish_engulfing(candles, index=1) is False
