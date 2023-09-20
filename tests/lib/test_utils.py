import pytest
from hexital.lib.utils import candles_sum


def test_candle_sum_reg_close(minimal_candles):
    assert candles_sum(minimal_candles, "close", length=2) == 19904


def test_candle_sum_reg_close_all(minimal_candles):
    assert candles_sum(minimal_candles, "close", length=9) == 104074


def test_candle_sum_reg_indicator(minimal_candles):
    assert candles_sum(minimal_candles, "ATR", length=3) == 5700


def test_candle_sum_reg_indicator_inverse_length(minimal_candles):
    assert candles_sum(minimal_candles, "ATR", length=3, index=-3) == 5100


def test_candle_sum_reg_indicator_insane_index(minimal_candles):
    assert candles_sum(minimal_candles, "ATR", length=3, index=100) == 5700


def test_candle_sum_reg_indicator_insane_index_and_length(minimal_candles):
    assert candles_sum(minimal_candles, "ATR", length=100, index=100) == 21000
