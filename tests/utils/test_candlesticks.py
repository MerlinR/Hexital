from typing import List

import pytest
from hexital.core import Candle
from hexital.utils.candlesticks import (
    candles_sum,
    reading_by_index,
    reading_count,
    reading_period,
)


class TestReadByIndex:
    @pytest.mark.usefixtures("minimal_candles")
    def test_basic(self, minimal_candles: List[Candle]):
        assert reading_by_index(minimal_candles, "high") == 10767

    def test_basic_invalid(self):
        assert reading_by_index([], "high") is None

    @pytest.mark.usefixtures("minimal_candles")
    def test_indexed(self, minimal_candles: List[Candle]):
        assert reading_by_index(minimal_candles, "high", index=5) == 5858

    @pytest.mark.usefixtures("minimal_candles")
    def test_indexed_invalid(self, minimal_candles: List[Candle]):
        assert reading_by_index(minimal_candles, "high", index=6000) is None

    @pytest.mark.usefixtures("minimal_candles")
    def test_indicator(self, minimal_candles: List[Candle]):
        assert reading_by_index(minimal_candles, "ATR") == 2000

    @pytest.mark.usefixtures("minimal_candles")
    def test_nested_indicator(self, minimal_candles: List[Candle]):
        assert reading_by_index(minimal_candles, "NATR") == {"nested": 2001}

    @pytest.mark.usefixtures("minimal_candles")
    def test_inner_nested_indicator(self, minimal_candles: List[Candle]):
        assert reading_by_index(minimal_candles, "NATR.nested") == 2001

    @pytest.mark.usefixtures("minimal_candles")
    def test_indicator_indexed(self, minimal_candles: List[Candle]):
        assert reading_by_index(minimal_candles, "ATR", index=5) == 600

    @pytest.mark.usefixtures("minimal_candles")
    def test_nested_indicator_indexed(self, minimal_candles: List[Candle]):
        assert reading_by_index(minimal_candles, "NATR", index=5) == {"nested": 601}

    @pytest.mark.usefixtures("minimal_candles")
    def test_inner_nested_indicator_indexed(self, minimal_candles: List[Candle]):
        assert reading_by_index(minimal_candles, "NATR.nested", index=5) == 601

    @pytest.mark.usefixtures("minimal_candles")
    def test_subindicator(self, minimal_candles: List[Candle]):
        assert reading_by_index(minimal_candles, "SATR") == 2010

    @pytest.mark.usefixtures("minimal_candles")
    def test_nested_subindicator(self, minimal_candles: List[Candle]):
        assert reading_by_index(minimal_candles, "SSATR") == {"nested": 2011}

    @pytest.mark.usefixtures("minimal_candles")
    def test_inner_nested_subindicator(self, minimal_candles: List[Candle]):
        assert reading_by_index(minimal_candles, "SSATR.nested") == 2011

    @pytest.mark.usefixtures("minimal_candles")
    def test_subindicator_indexed(self, minimal_candles: List[Candle]):
        assert reading_by_index(minimal_candles, "SATR", index=5) == 610

    @pytest.mark.usefixtures("minimal_candles")
    def test_nested_subindicator_indexed(self, minimal_candles: List[Candle]):
        assert reading_by_index(minimal_candles, "SSATR", index=5) == {"nested": 611}

    @pytest.mark.usefixtures("minimal_candles")
    def test_inner_nested_subindicator_indexed(self, minimal_candles: List[Candle]):
        assert reading_by_index(minimal_candles, "SSATR.nested", index=5) == 611


@pytest.mark.usefixtures("minimal_candles")
def test_reading_count(minimal_candles: List[Candle]):
    assert reading_count(minimal_candles, "open") == 20


@pytest.mark.usefixtures("minimal_candles")
def test_reading_count_limited(minimal_candles: List[Candle]):
    assert reading_count(minimal_candles, "MinTR") == 10


@pytest.mark.usefixtures("minimal_candles")
def test_reading_period(minimal_candles: List[Candle]):
    assert reading_period(minimal_candles, 5, "MinTR") is True


@pytest.mark.usefixtures("minimal_candles")
def test_reading_period_over(minimal_candles: List[Candle]):
    assert reading_period(minimal_candles, 15, "MinTR") is False


@pytest.mark.usefixtures("minimal_candles")
def test_reading_period_over_indexed(minimal_candles: List[Candle]):
    assert reading_period(minimal_candles, 5, "MinTR", 10) is False


@pytest.mark.usefixtures("minimal_candles")
def test_candle_sum_reg_close(minimal_candles):
    assert candles_sum(minimal_candles, "close", length=2) == 19904


@pytest.mark.usefixtures("minimal_candles")
def test_candle_sum_reg_close_all(minimal_candles):
    assert candles_sum(minimal_candles, "close", length=9) == 104074


@pytest.mark.usefixtures("minimal_candles")
def test_candle_sum_reg_indicator(minimal_candles):
    assert candles_sum(minimal_candles, "ATR", length=3) == 5700


@pytest.mark.usefixtures("minimal_candles")
def test_candle_sum_reg_indicator_inverse_length(minimal_candles):
    assert candles_sum(minimal_candles, "ATR", length=3, index=-3) == 5100


@pytest.mark.usefixtures("minimal_candles")
def test_candle_sum_reg_indicator_insane_index(minimal_candles):
    assert candles_sum(minimal_candles, "ATR", length=3, index=100) is None


@pytest.mark.usefixtures("minimal_candles")
def test_candle_sum_reg_indicator_insane_index_and_length(minimal_candles):
    assert candles_sum(minimal_candles, "ATR", length=100, index=100) is None
