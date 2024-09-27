from datetime import timedelta
from typing import List

import pytest
from hexital.core.candle import Candle
from hexital.utils.candles import (
    candles_sum,
    get_candles_period,
    get_candles_timeframe,
    get_readings_period,
    get_readings_timeframe,
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
def test_reading_count_index(minimal_candles: List[Candle]):
    assert reading_count(minimal_candles, "open", 1) == 2


@pytest.mark.usefixtures("minimal_candles")
def test_reading_count_index_two(minimal_candles: List[Candle]):
    assert reading_count(minimal_candles, "MinTR", 5) == 0


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
def test_reading_period_over_none(minimal_candles: List[Candle]):
    assert reading_period(minimal_candles, 6, "NoneATR", 5) is True


@pytest.mark.usefixtures("minimal_candles")
def test_reading_period_over_none_nested(minimal_candles: List[Candle]):
    assert reading_period(minimal_candles, 6, "NoneATR.nested", 5) is False


@pytest.mark.usefixtures("minimal_candles")
def test_reading_period_over_none_nested_two(minimal_candles: List[Candle]):
    assert reading_period(minimal_candles, 5, "NoneATR.nested", 5) is True


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
    assert candles_sum(minimal_candles, "ATR", length=3, index=100) == 5700


@pytest.mark.usefixtures("minimal_candles")
def test_candle_sum_reg_indicator_insane_index_and_length(minimal_candles):
    assert candles_sum(minimal_candles, "ATR", length=100, index=100) == 21000


class TestReadingsPeriod:
    @pytest.mark.usefixtures("minimal_candles")
    def test_basic(self, minimal_candles: List[Candle]):
        assert get_readings_period(minimal_candles, "high", 5, -1) == [
            5167,
            1398,
            3624,
            11555,
            4309,
        ]

    def test_basic_with_latest(self, minimal_candles: List[Candle]):
        assert get_readings_period(minimal_candles, "high", 5, -1, True) == [
            1398,
            3624,
            11555,
            4309,
            10767,
        ]


class TestCandlePeriod:
    @pytest.mark.usefixtures("minimal_candles")
    def test_basic(self, minimal_candles: List[Candle]):
        assert get_candles_period(minimal_candles, 5, -1) == minimal_candles[-6:-1]

    def test_basic_with_latest(self, minimal_candles: List[Candle]):
        assert get_candles_period(minimal_candles, 5, -1, True) == minimal_candles[-5:]


class TestReadingsTimeframe:
    @pytest.mark.usefixtures("minimal_candles")
    def test_basic(self, minimal_candles: List[Candle]):
        assert get_readings_timeframe(minimal_candles, "high", timedelta(minutes=4), -1) == [
            1398,
            3624,
            11555,
            4309,
        ]

    def test_basic_with_latest(self, minimal_candles: List[Candle]):
        assert get_readings_timeframe(minimal_candles, "high", timedelta(minutes=4), -1, True) == [
            1398,
            3624,
            11555,
            4309,
            10767,
        ]

    def test_solo(self, minimal_candles: List[Candle]):
        assert get_readings_timeframe(
            [minimal_candles[-1]], "high", timedelta(minutes=4), -1, True
        ) == [minimal_candles[-1].high]


class TestCandleTimeframe:
    @pytest.mark.usefixtures("minimal_candles")
    def test_basic(self, minimal_candles: List[Candle]):
        assert (
            get_candles_timeframe(minimal_candles, timedelta(minutes=4), -1)
            == minimal_candles[-5:-1]
        )

    def test_basic_with_latest(self, minimal_candles: List[Candle]):
        assert (
            get_candles_timeframe(minimal_candles, timedelta(minutes=4), -1, True)
            == minimal_candles[-5:]
        )

    def test_solo(self, minimal_candles: List[Candle]):
        assert get_candles_timeframe([minimal_candles[0]], timedelta(minutes=4), -1, True) == [
            minimal_candles[0]
        ]

    def test_rounded(self, minimal_candles: List[Candle]):
        assert (
            get_candles_timeframe(minimal_candles, timedelta(minutes=5), -1, True, True)
            == minimal_candles[-5:]
        )

    def test_rounded_two(self, minimal_candles: List[Candle]):
        assert (
            get_candles_timeframe(minimal_candles, timedelta(minutes=5), -3, True, True)
            == minimal_candles[-5:-2]
        )
