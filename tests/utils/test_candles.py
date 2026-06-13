from datetime import datetime

import pytest
from hexital.core.candle import Candle
from hexital.utils.candles import (
    candles_sum,
    get_readings_period,
    parse_candles,
    reading_by_index,
    reading_count,
    reading_period,
)


class TestReadByIndex:
    def test_basic(self, minimal_candles: list[Candle]):
        assert reading_by_index(minimal_candles, "high") == 10767

    def test_basic_invalid(self):
        assert reading_by_index([], "high") is None

    def test_indexed(self, minimal_candles: list[Candle]):
        assert reading_by_index(minimal_candles, "high", index=5) == 5858

    def test_indexed_invalid(self, minimal_candles: list[Candle]):
        assert reading_by_index(minimal_candles, "high", index=6000) is None

    def test_indicator(self, minimal_candles: list[Candle]):
        assert reading_by_index(minimal_candles, "ATR") == 2000

    def test_nested_indicator(self, minimal_candles: list[Candle]):
        assert reading_by_index(minimal_candles, "NATR") == {"nested": 2001}

    def test_inner_nested_indicator(self, minimal_candles: list[Candle]):
        assert reading_by_index(minimal_candles, "NATR.nested") == 2001

    def test_indicator_indexed(self, minimal_candles: list[Candle]):
        assert reading_by_index(minimal_candles, "ATR", index=5) == 600

    def test_nested_indicator_indexed(self, minimal_candles: list[Candle]):
        assert reading_by_index(minimal_candles, "NATR", index=5) == {"nested": 601}

    def test_inner_nested_indicator_indexed(self, minimal_candles: list[Candle]):
        assert reading_by_index(minimal_candles, "NATR.nested", index=5) == 601

    def test_subindicator(self, minimal_candles: list[Candle]):
        assert reading_by_index(minimal_candles, "SATR") == 2010

    def test_nested_subindicator(self, minimal_candles: list[Candle]):
        assert reading_by_index(minimal_candles, "SSATR") == {"nested": 2011}

    def test_inner_nested_subindicator(self, minimal_candles: list[Candle]):
        assert reading_by_index(minimal_candles, "SSATR.nested") == 2011

    def test_subindicator_indexed(self, minimal_candles: list[Candle]):
        assert reading_by_index(minimal_candles, "SATR", index=5) == 610

    def test_nested_subindicator_indexed(self, minimal_candles: list[Candle]):
        assert reading_by_index(minimal_candles, "SSATR", index=5) == {"nested": 611}

    def test_inner_nested_subindicator_indexed(self, minimal_candles: list[Candle]):
        assert reading_by_index(minimal_candles, "SSATR.nested", index=5) == 611


class TestParseCandles:
    def test_append_candle(self, minimal_candles):
        new_candle = minimal_candles[-1]

        candles = parse_candles(new_candle)

        assert candles == [
            Candle(
                open=2424,
                high=10767,
                low=13115,
                close=13649,
                volume=15750,
                indicators={"ATR": 2000, "NATR": {"nested": 2001}, "MinTR": 2002},
                sub_indicators={"SATR": 2010, "SSATR": {"nested": 2011}},
                timestamp=datetime(2023, 6, 1, 9, 19, 0),
            ),
        ]

    def test_append_list_nada(self):
        candles = parse_candles([])
        assert candles == []

    def test_append_candle_list(self, minimal_candles):
        candles = parse_candles(minimal_candles)

        assert candles == minimal_candles

    def test_append_candle_list_single(self, minimal_candles):
        candles = parse_candles([minimal_candles[-1]])

        assert candles == [
            Candle(
                open=2424,
                high=10767,
                low=13115,
                close=13649,
                volume=15750,
                indicators={"ATR": 2000, "NATR": {"nested": 2001}, "MinTR": 2002},
                sub_indicators={"SATR": 2010, "SSATR": {"nested": 2011}},
                timestamp=datetime(2023, 6, 1, 9, 19, 0),
            ),
        ]

    def test_append_dict(self):
        candles = parse_candles(
            {
                "open": 17213,
                "high": 2395,
                "low": 7813,
                "close": 3615,
                "volume": 19661,
                "timestamp": datetime(2023, 10, 3, 9, 0),
            }
        )

        assert candles == [
            Candle(
                17213,
                2395,
                7813,
                3615,
                19661,
                timestamp=datetime(2023, 10, 3, 9, 0),
            )
        ]

    def test_append_dict_list(self):
        candles = parse_candles(
            [
                {
                    "open": 17213,
                    "high": 2395,
                    "low": 7813,
                    "close": 3615,
                    "volume": 19661,
                    "timestamp": datetime(2023, 10, 3, 9, 0),
                },
                {
                    "open": 1301,
                    "high": 3007,
                    "low": 11626,
                    "close": 19048,
                    "volume": 28909,
                    "timestamp": datetime(2023, 10, 3, 9, 5),
                },
            ]
        )

        assert candles == [
            Candle(
                17213,
                2395,
                7813,
                3615,
                19661,
                timestamp=datetime(2023, 10, 3, 9, 0),
            ),
            Candle(
                1301,
                3007,
                11626,
                19048,
                28909,
                timestamp=datetime(2023, 10, 3, 9, 5),
            ),
        ]

    def test_append_list(self):
        candles = parse_candles(
            [datetime(2023, 10, 3, 9, 0), 17213, 2395, 7813, 3615, 19661]
        )

        assert candles == [
            Candle(17213, 2395, 7813, 3615, 19661, timestamp=datetime(2023, 10, 3, 9, 0))
        ]

    def test_append_list_list(self):
        candles = parse_candles(
            [
                [datetime(2023, 10, 3, 9, 0), 17213, 2395, 7813, 3615, 19661],
                [datetime(2023, 10, 3, 9, 5), 1301, 3007, 11626, 19048, 28909],
            ]
        )

        assert candles == [
            Candle(17213, 2395, 7813, 3615, 19661, timestamp=datetime(2023, 10, 3, 9, 0)),
            Candle(
                1301, 3007, 11626, 19048, 28909, timestamp=datetime(2023, 10, 3, 9, 5)
            ),
        ]

    def test_append_invalid(self):
        with pytest.raises(TypeError):
            parse_candles(["Fuck", 2, 3])


def test_reading_count(minimal_candles: list[Candle]):
    assert reading_count(minimal_candles, "open") == 20


def test_reading_count_limited(minimal_candles: list[Candle]):
    assert reading_count(minimal_candles, "MinTR") == 10


def test_reading_count_index(minimal_candles: list[Candle]):
    assert reading_count(minimal_candles, "open", 1) == 2


def test_reading_count_index_two(minimal_candles: list[Candle]):
    assert reading_count(minimal_candles, "MinTR", 5) == 0


def test_reading_period(minimal_candles: list[Candle]):
    assert reading_period(minimal_candles, "MinTR", 5) is True


def test_reading_period_over(minimal_candles: list[Candle]):
    assert reading_period(minimal_candles, "MinTR", 15) is False


def test_reading_period_over_indexed(minimal_candles: list[Candle]):
    assert reading_period(minimal_candles, "MinTR", 5, 10) is False


def test_reading_period_over_none(minimal_candles: list[Candle]):
    assert reading_period(minimal_candles, "NoneATR", 6, 5) is True


def test_reading_period_over_none_nested(minimal_candles: list[Candle]):
    assert reading_period(minimal_candles, "NoneATR.nested", 6, 5) is False


def test_reading_period_over_none_nested_two(minimal_candles: list[Candle]):
    assert reading_period(minimal_candles, "NoneATR.nested", 5, 5) is True


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


class TestReadingsPeriod:
    def test_basic(self, minimal_candles: list[Candle]):
        assert get_readings_period(minimal_candles, "high", 5, -1) == [
            5167,
            1398,
            3624,
            11555,
            4309,
        ]

    def test_basic_with_latest(self, minimal_candles: list[Candle]):
        assert get_readings_period(minimal_candles, "high", 5, -1, True) == [
            1398,
            3624,
            11555,
            4309,
            10767,
        ]
