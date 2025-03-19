from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List

import pytest
from hexital import Candle, Hexital, TimeFrame
from hexital.analysis.patterns import doji
from hexital.candlesticks.heikinashi import HeikinAshi
from hexital.core.hexital import HexitalCol
from hexital.core.indicator import Indicator
from hexital.core.indicator_collection import IndicatorCollection
from hexital.exceptions import (
    InvalidAnalysis,
    InvalidCandlestickType,
    InvalidIndicator,
)
from hexital.indicators import EMA, RMA, SMA, Amorph
from hexital.utils.candles import reading_by_candle
from tests.core.test_indicator import FakeIndicator


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
    def test_hextial_dict_diff_name(self, candles):
        strat = Hexital("Test Stratergy", candles, [{"indicator": "STDEV"}])
        assert strat.indicator("STDEV_30")

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


class TestAppend:
    @pytest.mark.usefixtures("candles")
    def test_append_timeframes(self, candles):
        strat = Hexital("Test Stratergy", [])
        strat.add_indicator([EMA(), EMA(timeframe="T5")])
        strat.append(candles[0])
        assert len(strat.candles("default")) == 1 and len(strat.candles("T5")) == 1
        strat.append(candles[-1], "T5")
        assert len(strat.candles("default")) == 1 and len(strat.candles("T5")) == 2
        strat.append(candles[-1], "default")
        assert len(strat.candles("default")) == 2 and len(strat.candles("T5")) == 2


class TestGetCandles:
    @pytest.mark.usefixtures("candles")
    def test_default(self, candles):
        strat = Hexital("Test Stratergy", [])
        strat.add_indicator([RMA(), EMA(timeframe="T5")])
        strat.append(candles)
        assert "RMA_10" in strat.candles()[-1].indicators

    @pytest.mark.usefixtures("candles")
    def test_default_specific(self, candles):
        strat = Hexital("Test Stratergy", [])
        strat.add_indicator([RMA(), EMA(timeframe="T5")])
        strat.append(candles)
        assert "RMA_10" in strat.candles("default")[-1].indicators

    @pytest.mark.usefixtures("candles")
    def test_by_indicator(self, candles):
        strat = Hexital("Test Stratergy", [])
        strat.add_indicator([RMA(), EMA(timeframe="T5")])
        strat.append(candles)
        assert "RMA_10" in strat.candles("RMA_10")[-1].indicators

    @pytest.mark.usefixtures("candles")
    def test_by_timeframe(self, candles):
        strat = Hexital("Test Stratergy", [])
        strat.add_indicator([RMA(), EMA(timeframe="T5")])
        strat.append(candles)
        assert "EMA_10_T5" in strat.candles("T5")[-1].indicators

    @pytest.mark.usefixtures("candles")
    def test_by_timeframe_timedelta(self, candles):
        strat = Hexital("Test Stratergy", [])
        strat.add_indicator([RMA(), EMA(timeframe="T5")])
        strat.append(candles)
        assert "EMA_10_T5" in strat.candles(timedelta(minutes=5))[-1].indicators


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
def test_hextial_readings(candles, expected_ema, expected_sma):
    strat = Hexital("Test Stratergy", candles, [EMA(), SMA()])
    strat.calculate()
    results = strat.readings()
    assert pytest.approx(results["SMA_10"]) == expected_sma
    assert pytest.approx(results["EMA_10"]) == expected_ema


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

    assert not strat.indicator("SMA_10")


@pytest.mark.usefixtures("candles")
def test_hextial_get_candles(candles):
    strat = Hexital("Test Stratergy", candles, [EMA()])
    strat.calculate()

    assert strat.candles()[-1].indicators.get("EMA_10")


class TestParseTimeframe:
    def test_hextial_parse_timeframe(self):
        strat = Hexital("Test Stratergy", [], [])
        assert strat._parse_timeframe(None) is None

    def test_hextial_parse_timeframe_two(self):
        strat = Hexital("Test Stratergy", [], [])
        assert strat._parse_timeframe("default") == "default"

    def test_hextial_parse_timeframe_three(self):
        strat = Hexital("Test Stratergy", [], [])
        assert strat._parse_timeframe(10) == "S10"

    def test_hextial_parse_timeframe_four(self):
        strat = Hexital("Test Stratergy", [], [])
        assert strat._parse_timeframe(timedelta(minutes=15)) == "T15"


@pytest.mark.usefixtures("minimal_candles")
def test_hextial_timerange(minimal_candles):
    strat = Hexital("Test Stratergy", [], candle_life=timedelta(minutes=1))

    strat.append(minimal_candles)

    assert strat.candles() == [
        Candle(
            open=16346,
            high=4309,
            low=1903,
            close=6255,
            volume=31307,
            timestamp=datetime(2023, 6, 1, 9, 18),
        ),
        Candle(
            open=2424,
            high=10767,
            low=13115,
            close=13649,
            volume=15750,
            timestamp=datetime(2023, 6, 1, 9, 19),
        ),
    ]


@pytest.mark.usefixtures("candles", "expected_ema")
def test_append_hexital_calc(candles, expected_ema):
    strat = Hexital("Test Stratergy", [], [{"indicator": "EMA"}])
    for candle in candles:
        strat.append(candle)
        strat.calculate()

    assert pytest.approx(strat.indicator("EMA_10").readings()) == expected_ema


@pytest.mark.usefixtures("candles", "expected_rsi")
def test_append_hexital_calc_sub_indicators(candles, expected_rsi):
    strat = Hexital("Test Stratergy", [], [{"indicator": "RSI", "period": 14}])

    for candle in candles:
        strat.append(candle)
        strat.calculate()
    assert pytest.approx(strat.indicator("RSI_14").readings()) == expected_rsi


class TestHexitalCandleManagerInheritance:
    @pytest.mark.usefixtures("candles")
    def test_hexital_inheritance(self, candles):
        strat = Hexital("Test Stratergy", candles, [EMA()], candle_life=timedelta(hours=1))

        assert strat.candle_life == timedelta(hours=1)
        assert strat.indicator("EMA_10").candle_life == timedelta(hours=1)

    @pytest.mark.usefixtures("candles")
    def test_hexital_inheritance_multi(self, candles):
        strat = Hexital(
            "Test Stratergy",
            candles,
            [EMA()],
            candle_life=timedelta(hours=1),
            timeframe=TimeFrame.MINUTE10,
        )

        assert strat.timeframe == "T10"
        assert strat.candle_life == timedelta(hours=1)
        assert strat.indicator("EMA_10").timeframe == "T10"
        assert strat.indicator("EMA_10").candle_life == timedelta(hours=1)

    @pytest.mark.usefixtures("candles")
    def test_hexital_inheritance_overriden(self, candles):
        strat = Hexital(
            "Test Stratergy",
            candles,
            [EMA(candle_life=timedelta(minutes=30))],
            candle_life=timedelta(hours=1),
        )

        assert strat.candle_life == timedelta(hours=1)
        assert strat.indicator("EMA_10").candle_life == timedelta(hours=1)

    @pytest.mark.usefixtures("candles")
    def test_hexital_inheritance_overriden_multi(self, candles):
        strat = Hexital(
            "Test Stratergy",
            candles,
            [EMA(timeframe="T10", candle_life=timedelta(minutes=30))],
            candle_life=timedelta(hours=1),
            timeframe="T5",
        )

        assert strat.candle_life == timedelta(hours=1)
        assert strat.timeframe == "T5"
        assert strat.indicator("EMA_10_T10").candle_life == timedelta(hours=1)
        assert strat.indicator("EMA_10_T10").timeframe == "T10"


class TestChain:
    @pytest.mark.usefixtures("candles")
    def test_hextial_movement(self, candles):
        strat = Hexital(
            "Test Stratergy",
            candles,
            [EMA(), EMA(source="EMA_10", name="Chained")],
        )
        strat.calculate()
        assert strat.has_reading("EMA_10") and strat.has_reading("Chained")


class TestCandlestickType:
    @pytest.mark.usefixtures("candles")
    def test_hextial_candlestick_type(self, candles):
        strat = Hexital("Test Stratergy", candles, [EMA()], candlestick=HeikinAshi())
        assert isinstance(strat.candlestick, HeikinAshi)

    @pytest.mark.usefixtures("candles")
    def test_hextial_candlestick_type_str(self, candles):
        strat = Hexital("Test Stratergy", candles, [EMA()], candlestick="HA")
        assert isinstance(strat.candlestick, HeikinAshi)

    @pytest.mark.usefixtures("candles")
    def test_hextial_candlestick_type_error(self, candles):
        with pytest.raises(InvalidCandlestickType):
            Hexital("Test Stratergy", candles, [EMA()], candlestick="FUCK")


class TestFindCandles:
    @pytest.mark.usefixtures("candles")
    def test_find_simple(self, candles):
        strat = Hexital("Test Stratergy", candles[:100], [EMA(name="EMA")])
        strat.calculate()

        assert strat.find_candles("EMA")

    @pytest.mark.usefixtures("candles")
    def test_find_missing(self, candles):
        strat = Hexital("Test Stratergy", candles[:100], [EMA(name="EMA")])
        strat.calculate()

        assert strat.find_candles("MMA") == [[], []]

    @pytest.mark.usefixtures("candles")
    def test_find_multi_simple(self, candles):
        strat = Hexital("Test Stratergy", candles[:100], [EMA(name="EMA"), SMA(name="SMA")])
        strat.calculate()

        found_candles = strat.find_candles("EMA", "SMA")

        assert found_candles[0] == found_candles[1]
        assert (
            reading_by_candle(found_candles[0][-1], "EMA") is not None
            and reading_by_candle(found_candles[0][-1], "SMA") is not None
        )

    @pytest.mark.usefixtures("candles")
    def test_find_multi_defaults_simple(self, candles):
        strat = Hexital("Test Stratergy", candles[:100], [EMA(name="EMA"), SMA(name="SMA")])
        strat.calculate()

        found_candles = strat.find_candles("EMA", "high")

        assert found_candles[0] == found_candles[1]
        assert (
            reading_by_candle(found_candles[0][-1], "EMA") is not None
            and reading_by_candle(found_candles[0][-1], "high") is not None
            and found_candles[0][-1].timeframe is None
        )

    @pytest.mark.usefixtures("candles")
    def test_find_rev_multi_defaults_simple(self, candles):
        strat = Hexital("Test Stratergy", candles[:100], [EMA(name="EMA"), SMA(name="SMA")])
        strat.calculate()

        found_candles = strat.find_candles("high", "EMA")

        assert found_candles[0] == found_candles[1]
        assert (
            reading_by_candle(found_candles[0][-1], "EMA") is not None
            and reading_by_candle(found_candles[0][-1], "high") is not None
            and found_candles[0][-1].timeframe is None
        )

    @pytest.mark.usefixtures("candles")
    def test_find_multi_timeframes(self, candles):
        strat = Hexital(
            "Test Stratergy",
            candles[:100],
            [EMA(name="EMA", timeframe="T5"), SMA(name="SMA", timeframe="T5")],
        )
        strat.calculate()

        found_candles = strat.find_candles("EMA", "SMA")

        assert found_candles[0] == found_candles[1]
        assert (
            reading_by_candle(found_candles[0][-1], "EMA") is not None
            and reading_by_candle(found_candles[0][-1], "SMA") is not None
        )

    @pytest.mark.usefixtures("candles")
    def test_find_multi_defaults_timeframes(self, candles):
        strat = Hexital(
            "Test Stratergy",
            candles[:100],
            timeframe="T5",
            indicators=[EMA(name="EMA"), SMA(name="SMA")],
        )
        strat.calculate()

        found_candles = strat.find_candles("EMA", "high")

        assert found_candles[0] == found_candles[1]
        assert (
            reading_by_candle(found_candles[0][-1], "EMA") is not None
            and reading_by_candle(found_candles[0][-1], "high") is not None
            and found_candles[0][-1].timeframe == timedelta(minutes=5)
        )

    @pytest.mark.usefixtures("candles")
    def test_find_multi_mixed_timeframes(self, candles):
        strat = Hexital(
            "Test Stratergy",
            candles[:100],
            [EMA(name="EMA"), SMA(name="SMA", timeframe="T5")],
        )
        strat.calculate()

        found_candles = strat.find_candles("SMA", "high")

        assert found_candles[0] == found_candles[1]
        assert (
            reading_by_candle(found_candles[0][-1], "SMA") is not None
            and reading_by_candle(found_candles[0][-1], "high") == strat.candles("SMA")[-1].high
            and found_candles[0][-1].timeframe == timedelta(minutes=5)
        )

    @pytest.mark.usefixtures("candles")
    def test_find_multi_rev_mixed_timeframes(self, candles):
        strat = Hexital(
            "Test Stratergy",
            candles[:100],
            [EMA(name="EMA"), SMA(name="SMA", timeframe="T5")],
        )
        strat.calculate()

        found_candles = strat.find_candles("high", "SMA")

        assert found_candles[0] == found_candles[1]
        assert (
            reading_by_candle(found_candles[0][-1], "SMA") is not None
            and reading_by_candle(found_candles[0][-1], "high") == strat.candles("SMA")[-1].high
            and found_candles[0][-1].timeframe == timedelta(minutes=5)
        )

    @pytest.mark.usefixtures("candles")
    def test_find_candles_multi_timeframes(self, candles):
        strat = Hexital(
            "Test Stratergy",
            candles,
            [EMA(name="EMA_T5", timeframe="T5"), EMA(name="EMA")],
        )
        strat.calculate()

        found_candles = strat.find_candles("EMA", "EMA_T5")

        assert len(found_candles) == 2
        assert (
            reading_by_candle(found_candles[0][-1], "EMA") is not None
            and reading_by_candle(found_candles[0][-1], "high") == strat.candles("EMA")[-1].high
            and found_candles[0][-1].timeframe is None
        )

        assert (
            reading_by_candle(found_candles[1][-1], "EMA_T5") is not None
            and reading_by_candle(found_candles[1][-1], "high") == strat.candles("EMA_T5")[-1].high
            and found_candles[1][-1].timeframe == timedelta(minutes=5)
        )


class TestMultiTimeframesNames:
    def test_timeframe_default(self, candles):
        strat = Hexital("Test Strategy", candles)
        assert list(strat._candles.keys()) == ["default"]

    def test_timeframe_multi(self, candles):
        strat = Hexital("Test Strategy", candles, [EMA(timeframe="T1")])
        assert list(strat._candles.keys()) == ["default", "T1"]

    def test_duplicate_indicators(self, candles):
        strat = Hexital("Test Strategy", candles, [EMA(timeframe="T1"), SMA(timeframe="T1")])
        assert list(strat._candles.keys()) == ["default", "T1"]

    def test_clash_hexital(self, candles):
        strat = Hexital("Test Strategy", candles, [EMA(timeframe="T1")], timeframe="T1")
        assert list(strat._candles.keys()) == ["T1"]

    def test_multi_hexital(self, candles):
        strat = Hexital("Test Strategy", candles, [EMA(timeframe="T5")], timeframe="T1")
        assert list(strat._candles.keys()) == ["T1", "T5"]


class TestHexitalSettings:
    def test_indicator_settings(self):
        strat = Hexital("Test Strategy", [], [EMA(candles=[])])

        assert strat.indicator_settings == [
            {
                "indicator": "EMA",
                "name": "EMA_10",
                "rounding": 4,
                "source": "close",
                "period": 10,
                "smoothing": 2.0,
            }
        ]

    def test_indicator_settings_with_amorph(self):
        strat = Hexital("Test Strategy", [], [EMA(candles=[]), Amorph(analysis=doji)])

        assert strat.indicator_settings == [
            {
                "indicator": "EMA",
                "name": "EMA_10",
                "rounding": 4,
                "source": "close",
                "period": 10,
                "smoothing": 2.0,
            },
            {
                "analysis": "doji",
                "name": "doji",
                "rounding": 4,
            },
        ]

    def test_hexital_settings(self):
        strat = Hexital(
            "Test Strategy",
            [],
            [EMA(candles=[])],
            timeframe="T5",
            candle_life=timedelta(minutes=60),
        )

        assert strat.settings == {
            "name": "Test Strategy",
            "candles": [],
            "candle_life": timedelta(seconds=3600),
            "timeframe": "T5",
            "timeframe_fill": False,
            "indicators": [
                {
                    "indicator": "EMA",
                    "name": "EMA_10",
                    "rounding": 4,
                    "source": "close",
                    "period": 10,
                    "smoothing": 2.0,
                }
            ],
        }

    def test_hexital_settings_back(self):
        as_dict = {
            "name": "Test Strategy",
            "candle_life": timedelta(seconds=3600),
            "timeframe": "T5",
            "timeframe_fill": False,
            "candles": [],
            "indicators": [
                {
                    "indicator": "EMA",
                    "name": "EMA_10",
                    "rounding": 4,
                    "source": "close",
                    "period": 10,
                    "smoothing": 2.0,
                }
            ],
        }
        strat = Hexital(**as_dict)

        assert strat.settings == as_dict


class TestIndicatorCollection:
    def test_collection(self, minimal_candles):
        @dataclass
        class customCol(IndicatorCollection):
            fake: Indicator = field(default_factory=FakeIndicator)

        collection = customCol()
        strat = Hexital("collection", minimal_candles, collection)

        assert strat.indicator("Fake_10")
        assert collection.fake.reading is not None

    def test_collectionRef(self, minimal_candles):
        @dataclass
        class customCol(IndicatorCollection):
            fake: Indicator = field(default_factory=FakeIndicator)

        strat = HexitalCol("collection", minimal_candles, customCol())

        assert strat.collection.fake
        assert strat.collection.fake.reading is not None
