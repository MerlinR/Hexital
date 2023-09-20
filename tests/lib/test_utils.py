import pytest
from hexital.lib.utils import candles_sum, round_values


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


def test_round_values_simple():
    assert round_values(100.696666) == 100.6967


def test_round_values_simple_int():
    assert round_values(100) == 100


def test_round_values_none():
    assert round_values(None) is None


def test_round_values_dict_simple():
    assert round_values({"one": 100.696666}) == {"one": 100.6967}


def test_round_values_dict_mixed():
    assert round_values({"one": 100.696666, "nada": None}) == {
        "one": 100.6967,
        "nada": None,
    }
