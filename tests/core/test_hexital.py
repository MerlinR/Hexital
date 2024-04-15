from datetime import datetime, timedelta
from typing import List

import pytest
from hexital import Candle, Hexital, TimeFrame
from hexital.candlesticks.heikinashi import HeikinAshi
from hexital.core.indicator import Indicator
from hexital.exceptions import (
    InvalidAnalysis,
    InvalidCandlestickType,
    InvalidIndicator,
)
from hexital.indicators import EMA, SMA


def fake_pattern(candles: List[Candle], index=-1):
    return 1


class TestIndicatorPattern:
    @pytest.mark.usefixtures("candles", "expected_ema")
    def test_hextial_single(self, candles, expected_ema):
        strat = Hexital("Test Stratergy", candles, [EMA()])
        strat.calculate()
        assert pytest.approx(strat.reading_as_list("EMA_10")) == expected_ema

    @pytest.mark.usefixtures("candles", "expected_ema", "expected_sma")
    def test_hextial_multi(self, candles, expected_ema, expected_sma):
        strat = Hexital("Test Stratergy", candles, [EMA(), SMA()])
        strat.calculate()
        assert (
            pytest.approx(strat.reading_as_list("EMA_10")) == expected_ema
            and pytest.approx(strat.reading_as_list("SMA_10")) == expected_sma
        )

    @pytest.mark.usefixtures("candles", "expected_sma")
    def test_hextial_dict(self, candles, expected_sma):
        strat = Hexital("Test Stratergy", candles, [{"indicator": "SMA"}])
        strat.calculate()
        assert pytest.approx(strat.reading_as_list("SMA_10")) == expected_sma

    @pytest.mark.usefixtures("candles", "expected_ema", "expected_sma")
    def test_hextial_mixed(self, candles, expected_ema, expected_sma):
        strat = Hexital("Test Stratergy", candles, [EMA(), {"indicator": "SMA"}])
        strat.calculate()
        assert (
            pytest.approx(strat.reading_as_list("EMA_10")) == expected_ema
            and pytest.approx(strat.reading_as_list("SMA_10")) == expected_sma
        )

    @pytest.mark.usefixtures("candles")
    def test_hextial_dict_arguments(self, candles):
        strat = Hexital("Test Stratergy", candles, [{"indicator": "SMA", "period": 20}])
        assert strat.indicator("SMA_20")

    @pytest.mark.usefixtures("candles")
    def test_hextial_dict_invalid(self, candles):
        with pytest.raises(InvalidIndicator):
            Hexital("Test Stratergy", candles, [{"indicator": "FUCK"}])

    @pytest.mark.usefixtures("candles")
    def test_hextial_dict_invalid_missing(self, candles):
        with pytest.raises(InvalidAnalysis):
            Hexital("Test Stratergy", candles, [{"period": 10}])

    @pytest.mark.usefixtures("candles", "expected_ema", "expected_sma")
    def test_hextial_dict_append(self, candles, expected_ema, expected_sma):
        strat = Hexital("Test Stratergy", candles, [EMA()])
        strat.add_indicator({"indicator": "SMA"})
        strat.calculate()
        assert (
            pytest.approx(strat.reading_as_list("EMA_10")) == expected_ema
            and pytest.approx(strat.reading_as_list("SMA_10")) == expected_sma
        )

    @pytest.mark.usefixtures("candles")
    def test_hextial_dict_analysis_pattern(self, candles):
        strat = Hexital("Test Stratergy", candles, [{"analysis": "doji"}])
        strat.calculate()
        assert strat.reading("doji") is not None

    @pytest.mark.usefixtures("candles")
    def test_hextial_dict_movement(self, candles):
        strat = Hexital("Test Stratergy", candles, [{"analysis": "positive"}])
        strat.calculate()
        assert strat.reading("positive") is not None

    @pytest.mark.usefixtures("candles")
    def test_hextial_dict_analysis_custom(self, candles):
        strat = Hexital("Test Stratergy", candles, [{"analysis": fake_pattern}])
        strat.calculate()
        assert strat.reading("fake_pattern") is not None


@pytest.mark.usefixtures("candles", "expected_ema")
def test_hextial_single(candles, expected_ema):
    strat = Hexital("Test Stratergy", candles)
    strat.add_indicator(EMA())
    strat.calculate()
    assert pytest.approx(strat.reading_as_list("EMA_10")) == expected_ema


@pytest.mark.usefixtures("candles", "expected_ema", "expected_sma")
def test_hextial_multi(candles, expected_ema, expected_sma):
    strat = Hexital("Test Stratergy", candles, [EMA(), SMA()])
    strat.calculate()
    assert (
        pytest.approx(strat.reading_as_list("EMA_10")) == expected_ema
        and pytest.approx(strat.reading_as_list("SMA_10")) == expected_sma
    )


@pytest.mark.usefixtures("candles", "expected_sma")
def test_hextial_reading(candles, expected_sma):
    strat = Hexital("Test Stratergy", candles, [{"indicator": "SMA", "period": 10}])
    strat.calculate()
    assert pytest.approx(strat.reading("SMA_10")) == expected_sma[-1]


@pytest.mark.usefixtures("candles", "expected_sma")
def test_hextial_prev_reading(candles, expected_sma):
    strat = Hexital("Test Stratergy", candles, [{"indicator": "SMA", "period": 10}])
    strat.calculate()
    assert pytest.approx(strat.prev_reading("SMA_10")) == expected_sma[-2]


@pytest.mark.usefixtures("candles")
def test_hextial_has_reading(candles):
    strat = Hexital("Test Stratergy", candles, [{"indicator": "SMA", "period": 10}])
    assert strat.has_reading("SMA_10") is False

    strat.calculate()
    assert strat.has_reading("SMA_10")


@pytest.mark.usefixtures("candles")
def test_hextial_has_reading_exists_no_values(candles):
    strat = Hexital("Test Stratergy", candles, [{"indicator": "SMA", "period": 10}])
    assert strat.has_reading("SMA_10") is False


@pytest.mark.usefixtures("candles")
def test_hextial_has_reading_missing(candles):
    strat = Hexital("Test Stratergy", candles, [{"indicator": "SMA", "period": 10}])
    strat.calculate()
    assert strat.has_reading("EMA") is False


@pytest.mark.usefixtures("candles")
def test_hextial_indicator_selection(candles):
    strat = Hexital("Test Stratergy", candles, [{"indicator": "SMA", "period": 10}])
    strat.calculate()
    assert isinstance(strat.indicator("SMA_10"), Indicator)


@pytest.mark.usefixtures("candles", "expected_ema", "expected_sma")
def test_hextial_purge(candles, expected_ema, expected_sma):
    strat = Hexital("Test Stratergy", candles, [EMA(), {"indicator": "SMA"}])
    strat.calculate()

    assert strat.has_reading("SMA_10") and strat.has_reading("EMA_10")
    strat.purge("SMA_10")

    assert not strat.has_reading("SMA_10") and strat.has_reading("EMA_10")


@pytest.mark.usefixtures("candles", "expected_ema", "expected_sma")
def test_hextial_remove_indicator(candles, expected_ema, expected_sma):
    strat = Hexital("Test Stratergy", candles, [EMA(), {"indicator": "SMA"}])
    strat.calculate()

    assert strat.has_reading("SMA_10")

    strat.remove_indicator("SMA_10")

    assert not strat.indicators.get("SMA_10")


@pytest.mark.usefixtures("candles")
def test_hextial_get_candles(candles):
    strat = Hexital("Test Stratergy", candles, [EMA()])
    strat.calculate()

    assert strat.candles()[-1].indicators.get("EMA_10")


@pytest.mark.usefixtures("minimal_candles")
def test_hextial_timerange(minimal_candles):
    strat = Hexital("Test Stratergy", [], candles_lifespan=timedelta(minutes=1))

    strat.append(minimal_candles)

    assert strat.candles() == [
        Candle(
            open=16346,
            high=4309,
            low=1903,
            close=6255,
            volume=31307,
            indicators={"ATR": 1900, "MinTR": 1902, "NATR": {"nested": 1901}},
            sub_indicators={"SATR": 1910, "SSATR": {"nested": 1911}},
            timestamp=datetime(2023, 6, 1, 9, 18),
        ),
        Candle(
            open=2424,
            high=10767,
            low=13115,
            close=13649,
            volume=15750,
            indicators={"ATR": 2000, "MinTR": 2002, "NATR": {"nested": 2001}},
            sub_indicators={"SATR": 2010, "SSATR": {"nested": 2011}},
            timestamp=datetime(2023, 6, 1, 9, 19),
        ),
    ]


@pytest.mark.usefixtures("candles", "expected_ema")
def test_append_hexital_calc(candles, expected_ema):
    strat = Hexital("Test Stratergy", [], [{"indicator": "EMA"}])
    for candle in candles:
        strat.append(candle)
        strat.calculate()

    assert pytest.approx(strat.indicator("EMA_10").as_list()) == expected_ema


@pytest.mark.usefixtures("candles", "expected_rsi")
def test_append_hexital_calc_sub_indicators(candles, expected_rsi):
    strat = Hexital("Test Stratergy", [], [{"indicator": "RSI", "period": 14}])

    for candle in candles:
        strat.append(candle)
        strat.calculate()
    assert pytest.approx(strat.indicator("RSI_14").as_list()) == expected_rsi


class TestHexitalCandleManagerInheritance:
    @pytest.mark.usefixtures("candles")
    def test_hexital_inheritance(self, candles):
        strat = Hexital("Test Stratergy", candles, [EMA()], candles_lifespan=timedelta(hours=1))

        assert strat.candles_lifespan == timedelta(hours=1)
        assert strat.indicator("EMA_10").candles_lifespan == timedelta(hours=1)

    @pytest.mark.usefixtures("candles")
    def test_hexital_inheritance_multi(self, candles):
        strat = Hexital(
            "Test Stratergy",
            candles,
            [EMA()],
            candles_lifespan=timedelta(hours=1),
            timeframe=TimeFrame.MINUTE10,
        )

        assert strat.timeframe == "T10"
        assert strat.candles_lifespan == timedelta(hours=1)
        assert strat.indicator("EMA_10").timeframe == "T10"
        assert strat.indicator("EMA_10").candles_lifespan == timedelta(hours=1)

    @pytest.mark.usefixtures("candles")
    def test_hexital_inheritance_overriden(self, candles):
        strat = Hexital(
            "Test Stratergy",
            candles,
            [EMA(candles_lifespan=timedelta(minutes=30))],
            candles_lifespan=timedelta(hours=1),
        )

        assert strat.candles_lifespan == timedelta(hours=1)
        assert strat.indicator("EMA_10").candles_lifespan == timedelta(hours=1)

    @pytest.mark.usefixtures("candles")
    def test_hexital_inheritance_overriden_multi(self, candles):
        strat = Hexital(
            "Test Stratergy",
            candles,
            [EMA(timeframe="T10", candles_lifespan=timedelta(minutes=30))],
            candles_lifespan=timedelta(hours=1),
            timeframe="T5",
        )

        assert strat.candles_lifespan == timedelta(hours=1)
        assert strat.timeframe == "T5"
        assert strat.indicator("EMA_10_T10").candles_lifespan == timedelta(hours=1)
        assert strat.indicator("EMA_10_T10").timeframe == "T10"


class TestChain:
    @pytest.mark.usefixtures("candles")
    def test_hextial_movement(self, candles):
        strat = Hexital(
            "Test Stratergy",
            candles,
            [EMA(), EMA(input_value="EMA_10", fullname_override="Chained")],
        )
        strat.calculate()
        assert strat.has_reading("EMA_10") and strat.has_reading("Chained")


class TestCandlestickType:
    @pytest.mark.usefixtures("candles")
    def test_hextial_candlestick_type(self, candles):
        strat = Hexital("Test Stratergy", candles, [EMA()], candlestick_type=HeikinAshi())
        assert isinstance(strat.candlestick_type, HeikinAshi)

    @pytest.mark.usefixtures("candles")
    def test_hextial_candlestick_type_str(self, candles):
        strat = Hexital("Test Stratergy", candles, [EMA()], candlestick_type="HA")
        assert isinstance(strat.candlestick_type, HeikinAshi)

    @pytest.mark.usefixtures("candles")
    def test_hextial_candlestick_type_error(self, candles):
        with pytest.raises(InvalidCandlestickType):
            Hexital("Test Stratergy", candles, [EMA()], candlestick_type="FUCK")
