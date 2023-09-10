import pytest
from hexital.core.candle import Candle
from hexital.lib.utils import candles_sum


@pytest.fixture(name="rising_candles")
def fixture_rising_candles():
    return [
        Candle(open=90, high=110, low=80, close=80, volume=10, indicators={"ATR": 600}),
        Candle(open=100, high=120, low=90, close=90, volume=10, indicators={"ATR": 700}),
        Candle(
            open=110, high=130, low=100, close=100, volume=10, indicators={"ATR": 800}
        ),
        Candle(
            open=120, high=140, low=110, close=110, volume=10, indicators={"ATR": 900}
        ),
        Candle(
            open=130, high=150, low=120, close=120, volume=10, indicators={"ATR": 990}
        ),
    ]


def test_candle_sum_reg_close(rising_candles):
    assert candles_sum(rising_candles, "close", length=2) == 230


def test_candle_sum_reg_close_all(rising_candles):
    assert candles_sum(rising_candles, "close", length=9) == 500


def test_candle_sum_reg_indicator(rising_candles):
    assert candles_sum(rising_candles, "ATR", length=3) == 2690


def test_candle_sum_reg_indicator_inverse_length(rising_candles):
    assert candles_sum(rising_candles, "ATR", length=3, index=-3) == 2400


def test_candle_sum_reg_indicator_insane_index(rising_candles):
    assert candles_sum(rising_candles, "ATR", length=3, index=100) == 2690


def test_candle_sum_reg_indicator_insane_index_and_length(rising_candles):
    assert candles_sum(rising_candles, "ATR", length=100, index=100) == 3990


def test_candle_sum_reg_indicator_blank(rising_candles):
    assert candles_sum(rising_candles, "ATR") == 990
