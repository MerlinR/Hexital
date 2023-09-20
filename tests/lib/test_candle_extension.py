from typing import List

import pytest
from hexital.core import Candle
from hexital.lib.candle_extension import (
    reading_as_list,
    reading_by_index,
    reading_count,
    reading_period,
)


class TestReadByIndex:
    @pytest.mark.usefixtures("minimal_candles")
    def test_basic(self, minimal_candles: List[Candle]):
        assert reading_by_index(minimal_candles, "high") == 10767

    @pytest.mark.usefixtures("minimal_candles")
    def test_indexed(self, minimal_candles: List[Candle]):
        assert reading_by_index(minimal_candles, "high", index=5) == 5858

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
def test_reading_as_list_exp(minimal_candles: List[Candle]):
    assert reading_as_list(minimal_candles, "ATR") == [
        100,
        200,
        300,
        400,
        500,
        600,
        700,
        800,
        900,
        1000,
        1100,
        1200,
        1300,
        1400,
        1500,
        1600,
        1700,
        1800,
        1900,
        2000,
    ]


@pytest.mark.usefixtures("minimal_candles")
def test_reading_as_list_partial(minimal_candles: List[Candle]):
    assert reading_as_list(minimal_candles, "MinTR") == [
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        1102,
        1202,
        1302,
        1402,
        1502,
        1602,
        1702,
        1802,
        1902,
        2002,
    ]


@pytest.mark.usefixtures("minimal_candles")
def test_reading_as_list_no_indicator(minimal_candles: List[Candle]):
    assert reading_as_list(minimal_candles, "FUCK") == [None] * 20


@pytest.mark.usefixtures("minimal_candles")
def test_reading_period(minimal_candles: List[Candle]):
    assert reading_period(minimal_candles, 5, "MinTR") is True


@pytest.mark.usefixtures("minimal_candles")
def test_reading_period_over(minimal_candles: List[Candle]):
    assert reading_period(minimal_candles, 15, "MinTR") is False


@pytest.mark.usefixtures("minimal_candles")
def test_reading_period_over_indexed(minimal_candles: List[Candle]):
    assert reading_period(minimal_candles, 5, "MinTR", 10) is False
