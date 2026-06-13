from dataclasses import dataclass, field
from datetime import datetime, timedelta

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


def fake_pattern(candles: list[Candle], index=-1):
    return 1


class TestIndicatorPattern:
    def test_hextial_single(self, candles, expected_ema):
        strategy = Hexital("Test Stratergy", candles, [EMA()])
        strategy.calculate()
        assert pytest.approx(strategy.reading_as_list("EMA_10")) == expected_ema

    def test_hextial_multi(self, candles, expected_ema, expected_sma):
        strategy = Hexital("Test Stratergy", candles, [EMA(), SMA()])
        strategy.calculate()
        assert (
            pytest.approx(strategy.reading_as_list("EMA_10")) == expected_ema
            and pytest.approx(strategy.reading_as_list("SMA_10")) == expected_sma
        )

    def test_hextial_dict(self, candles, expected_sma):
        strategy = Hexital("Test Stratergy", candles, [{"indicator": "SMA"}])
        strategy.calculate()
        assert pytest.approx(strategy.reading_as_list("SMA_10")) == expected_sma

    def test_hextial_mixed(self, candles, expected_ema, expected_sma):
        strategy = Hexital("Test Stratergy", candles, [EMA(), {"indicator": "SMA"}])
        strategy.calculate()
        assert (
            pytest.approx(strategy.reading_as_list("EMA_10")) == expected_ema
            and pytest.approx(strategy.reading_as_list("SMA_10")) == expected_sma
        )

    def test_hextial_dict_diff_name(self, candles):
        strategy = Hexital("Test Stratergy", candles, [{"indicator": "STDEV"}])
        assert strategy.indicator("STDEV_30")

    def test_hextial_dict_arguments(self, candles):
        strategy = Hexital(
            "Test Stratergy", candles, [{"indicator": "SMA", "period": 20}]
        )
        assert strategy.indicator("SMA_20")

    def test_hextial_dict_invalid(self, candles):
        with pytest.raises(InvalidIndicator):
            Hexital("Test Stratergy", candles, [{"indicator": "FUCK"}])

    def test_hextial_dict_invalid_missing(self, candles):
        with pytest.raises(InvalidAnalysis):
            Hexital("Test Stratergy", candles, [{"period": 10}])

    def test_hextial_dict_append(self, candles, expected_ema, expected_sma):
        strategy = Hexital("Test Stratergy", candles, [EMA()])
        strategy.add_indicator({"indicator": "SMA"})
        strategy.calculate()
        assert (
            pytest.approx(strategy.reading_as_list("EMA_10")) == expected_ema
            and pytest.approx(strategy.reading_as_list("SMA_10")) == expected_sma
        )

    def test_hextial_dict_analysis_pattern(self, candles):
        strategy = Hexital("Test Stratergy", candles, [{"analysis": "doji"}])
        strategy.calculate()
        assert strategy.reading("doji") is not None

    def test_hextial_dict_movement(self, candles):
        strategy = Hexital("Test Stratergy", candles, [{"analysis": "positive"}])
        strategy.calculate()
        assert strategy.reading("positive") is not None

    def test_hextial_dict_analysis_custom(self, candles):
        strategy = Hexital("Test Stratergy", candles, [{"analysis": fake_pattern}])
        strategy.calculate()
        assert strategy.reading("fake_pattern") is not None


class TestAppend:
    def test_append_timeframes(self, candles):
        strategy = Hexital("Test Stratergy", [])
        strategy.add_indicator([EMA(), EMA(timeframe="T5")])
        strategy.append(candles[0])
        assert len(strategy.candles()) == 1 and len(strategy.candles("T5")) == 1
        strategy.append(candles[-1])
        assert len(strategy.candles()) == 2 and len(strategy.candles("T5")) == 2


class TestGetCandles:
    def test_default(self, candles):
        strategy = Hexital("Test Stratergy", [])
        strategy.add_indicator([RMA(), EMA(timeframe="T5")])
        strategy.append(candles)
        assert "RMA_10" in strategy.candles()[-1].indicators

    def test_default_specific(self, candles):
        strategy = Hexital("Test Stratergy", [])
        strategy.add_indicator([RMA(), EMA(timeframe="T5")])
        strategy.append(candles)
        assert "RMA_10" in strategy.candles()[-1].indicators

    def test_by_indicator(self, candles):
        strategy = Hexital("Test Stratergy", [])
        strategy.add_indicator([RMA(), EMA(timeframe="T5")])
        strategy.append(candles)
        assert "RMA_10" in strategy.candles("RMA_10")[-1].indicators

    def test_by_timeframe(self, candles):
        strategy = Hexital("Test Stratergy", [])
        strategy.add_indicator([RMA(), EMA(timeframe="T5")])
        strategy.append(candles)
        assert "EMA_10_T5" in strategy.candles("T5")[-1].indicators

    def test_by_timeframe_timedelta(self, candles):
        strategy = Hexital("Test Stratergy", [])
        strategy.add_indicator([RMA(), EMA(timeframe="T5")])
        strategy.append(candles)
        assert "EMA_10_T5" in strategy.candles(timedelta(minutes=5))[-1].indicators


def test_hextial_single(candles, expected_ema):
    strategy = Hexital("Test Stratergy", candles)
    strategy.add_indicator(EMA())
    strategy.calculate()
    assert pytest.approx(strategy.reading_as_list("EMA_10")) == expected_ema


def test_hextial_multi(candles, expected_ema, expected_sma):
    strategy = Hexital("Test Stratergy", candles, [EMA(), SMA()])
    strategy.calculate()
    assert (
        pytest.approx(strategy.reading_as_list("EMA_10")) == expected_ema
        and pytest.approx(strategy.reading_as_list("SMA_10")) == expected_sma
    )


def test_hextial_reading(candles, expected_sma):
    strategy = Hexital("Test Stratergy", candles, [{"indicator": "SMA", "period": 10}])
    strategy.calculate()
    assert pytest.approx(strategy.reading("SMA_10")) == expected_sma[-1]


def test_hextial_prev_reading(candles, expected_sma):
    strategy = Hexital("Test Stratergy", candles, [{"indicator": "SMA", "period": 10}])
    strategy.calculate()
    assert pytest.approx(strategy.prev_reading("SMA_10")) == expected_sma[-2]


def test_hextial_has_reading(candles):
    strategy = Hexital("Test Stratergy", candles, [{"indicator": "SMA", "period": 10}])
    assert strategy.exists("SMA_10") is False

    strategy.calculate()
    assert strategy.exists("SMA_10")


def test_hextial_has_reading_exists_no_values(candles):
    strategy = Hexital("Test Stratergy", candles, [{"indicator": "SMA", "period": 10}])
    assert strategy.exists("SMA_10") is False


def test_hextial_has_reading_missing(candles):
    strategy = Hexital("Test Stratergy", candles, [{"indicator": "SMA", "period": 10}])
    strategy.calculate()
    assert strategy.exists("EMA") is False


def test_hextial_indicator_selection(candles):
    strategy = Hexital("Test Stratergy", candles, [{"indicator": "SMA", "period": 10}])
    strategy.calculate()
    assert isinstance(strategy.indicator("SMA_10"), Indicator)


def test_hextial_readings(candles, expected_ema, expected_sma):
    strategy = Hexital("Test Stratergy", candles, [EMA(), SMA()])
    strategy.calculate()
    results = strategy.readings()
    assert pytest.approx(results["SMA_10"]) == expected_sma
    assert pytest.approx(results["EMA_10"]) == expected_ema


def test_hextial_purge(candles, expected_ema, expected_sma):
    strategy = Hexital("Test Stratergy", candles, [EMA(), {"indicator": "SMA"}])
    strategy.calculate()

    assert strategy.exists("SMA_10") and strategy.exists("EMA_10")
    strategy.purge("SMA_10")

    assert not strategy.exists("SMA_10") and strategy.exists("EMA_10")


def test_hextial_remove_indicator(candles, expected_ema, expected_sma):
    strategy = Hexital("Test Stratergy", candles, [EMA(), {"indicator": "SMA"}])
    strategy.calculate()

    assert strategy.exists("SMA_10")

    strategy.remove_indicator("SMA_10")

    assert not strategy.indicator("SMA_10")


def test_hextial_get_candles(candles):
    strategy = Hexital("Test Stratergy", candles, [EMA()])
    strategy.calculate()

    assert strategy.candles()[-1].indicators.get("EMA_10")


def test_hextial_timerange(minimal_candles):
    strategy = Hexital("Test Stratergy", [], candle_life=timedelta(minutes=1))

    strategy.append(minimal_candles)

    assert strategy.candles() == [
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


def test_append_hexital_calc(candles, expected_ema):
    strategy = Hexital("Test Stratergy", [], [{"indicator": "EMA"}])
    for candle in candles:
        strategy.append(candle)
        strategy.calculate()

    assert pytest.approx(strategy.indicator("EMA_10").readings()) == expected_ema


def test_append_hexital_calc_sub_indicators(candles, expected_rsi):
    strategy = Hexital("Test Stratergy", [], [{"indicator": "RSI", "period": 14}])

    for candle in candles:
        strategy.append(candle)
        strategy.calculate()
    assert pytest.approx(strategy.indicator("RSI_14").readings()) == expected_rsi


class TestHexitalCandleManagerInheritance:
    def test_hexital_inheritance(self, candles):
        strategy = Hexital(
            "Test Stratergy", candles, [EMA()], candle_life=timedelta(hours=1)
        )

        assert strategy.candle_life == timedelta(hours=1)
        assert strategy.indicator("EMA_10").candle_life == timedelta(hours=1)

    def test_hexital_inheritance_multi(self, candles):
        strategy = Hexital(
            "Test Stratergy",
            candles,
            [EMA()],
            candle_life=timedelta(hours=1),
            timeframe=TimeFrame.MINUTE10,
        )

        assert strategy.timeframe == "T10"
        assert strategy.candle_life == timedelta(hours=1)
        assert strategy.indicator("EMA_10").timeframe == "T10"
        assert strategy.indicator("EMA_10").candle_life == timedelta(hours=1)

    def test_hexital_inheritance_overriden(self, candles):
        strategy = Hexital(
            "Test Stratergy",
            candles,
            [EMA(candle_life=timedelta(minutes=30))],
            candle_life=timedelta(hours=1),
        )

        assert strategy.candle_life == timedelta(hours=1)
        assert strategy.indicator("EMA_10").candle_life == timedelta(hours=1)

    def test_hexital_inheritance_overriden_multi(self, candles):
        strategy = Hexital(
            "Test Stratergy",
            candles,
            [EMA(timeframe="T10", candle_life=timedelta(minutes=30))],
            candle_life=timedelta(hours=1),
            timeframe="T5",
        )

        assert strategy.candle_life == timedelta(hours=1)
        assert strategy.timeframe == "T5"
        assert strategy.indicator("EMA_10_T10").candle_life == timedelta(hours=1)
        assert strategy.indicator("EMA_10_T10").timeframe == "T10"


class TestChain:
    def test_hextial_movement(self, candles):
        strategy = Hexital(
            "Test Stratergy",
            candles,
            [EMA(), EMA(source="EMA_10", name="Chained")],
        )
        strategy.calculate()
        assert strategy.exists("EMA_10") and strategy.exists("Chained")


class TestCandlestickType:
    def test_hextial_candlestick_type(self, candles):
        strategy = Hexital("Test Stratergy", candles, [EMA()], candlestick=HeikinAshi())
        assert isinstance(strategy.candlestick, HeikinAshi)

    def test_hextial_candlestick_type_str(self, candles):
        strategy = Hexital("Test Stratergy", candles, [EMA()], candlestick="HA")
        assert isinstance(strategy.candlestick, HeikinAshi)

    def test_hextial_candlestick_type_error(self, candles):
        with pytest.raises(InvalidCandlestickType):
            Hexital("Test Stratergy", candles, [EMA()], candlestick="FUCK")


class TestFindCandles:
    def test_find_simple(self, candles):
        strategy = Hexital("Test Stratergy", candles[:100], [EMA(name="EMA")])
        strategy.calculate()

        assert strategy.find_candle_pairing("EMA")

    def test_find_missing(self, candles):
        strategy = Hexital("Test Stratergy", candles[:100], [EMA(name="EMA")])
        strategy.calculate()

        assert strategy.find_candle_pairing("MMA") == ([], [])

    def test_find_multi_simple(self, candles):
        strategy = Hexital(
            "Test Stratergy", candles[:100], [EMA(name="EMA"), SMA(name="SMA")]
        )
        strategy.calculate()

        found_candles = strategy.find_candle_pairing("EMA", "SMA")

        assert found_candles[0] == found_candles[1]
        assert (
            reading_by_candle(found_candles[0][-1], "EMA") is not None
            and reading_by_candle(found_candles[0][-1], "SMA") is not None
        )

    def test_find_multi_defaults_simple(self, candles):
        strategy = Hexital(
            "Test Stratergy", candles[:100], [EMA(name="EMA"), SMA(name="SMA")]
        )
        strategy.calculate()

        found_candles = strategy.find_candle_pairing("EMA", "high")

        assert found_candles[0] == found_candles[1]

        assert (
            reading_by_candle(found_candles[0][-1], "EMA") is not None
            and reading_by_candle(found_candles[0][-1], "high") is not None
        )
        assert found_candles[0][-1].timeframe == timedelta(seconds=60)

    def test_find_rev_multi_defaults_simple(self, candles):
        strategy = Hexital(
            "Test Stratergy", candles[:100], [EMA(name="EMA"), SMA(name="SMA")]
        )
        strategy.calculate()

        found_candles = strategy.find_candle_pairing("high", "EMA")

        assert found_candles[0] == found_candles[1]
        assert (
            reading_by_candle(found_candles[0][-1], "EMA") is not None
            and reading_by_candle(found_candles[0][-1], "high") is not None
        )
        assert found_candles[0][-1].timeframe == timedelta(seconds=60)

    def test_find_multi_timeframes(self, candles):
        strategy = Hexital(
            "Test Stratergy",
            candles[:100],
            [EMA(name="EMA", timeframe="T5"), SMA(name="SMA", timeframe="T5")],
        )
        strategy.calculate()

        found_candles = strategy.find_candle_pairing("EMA", "SMA")

        assert found_candles[0] == found_candles[1]
        assert (
            reading_by_candle(found_candles[0][-1], "EMA") is not None
            and reading_by_candle(found_candles[0][-1], "SMA") is not None
        )

    def test_find_multi_defaults_timeframes(self, candles):
        strategy = Hexital(
            "Test Stratergy",
            candles[:100],
            timeframe="T5",
            indicators=[EMA(name="EMA"), SMA(name="SMA")],
        )
        strategy.calculate()

        found_candles = strategy.find_candle_pairing("EMA", "high")

        assert found_candles[0] == found_candles[1]
        assert (
            reading_by_candle(found_candles[0][-1], "EMA") is not None
            and reading_by_candle(found_candles[0][-1], "high") is not None
        )

        assert found_candles[0][-1].timeframe == timedelta(seconds=300)

    def test_find_multi_mixed_timeframes(self, candles):
        strategy = Hexital(
            "Test Stratergy",
            candles[:100],
            [EMA(name="EMA"), SMA(name="SMA", timeframe="T5")],
        )
        strategy.calculate()

        found_candles = strategy.find_candle_pairing("SMA", "high")

        assert found_candles[0] == found_candles[1]
        assert (
            reading_by_candle(found_candles[0][-1], "SMA") is not None
            and reading_by_candle(found_candles[0][-1], "high")
            == strategy.candles("SMA")[-1].high
            and found_candles[0][-1].timeframe == timedelta(seconds=300)
        )

    def test_find_multi_rev_mixed_timeframes(self, candles):
        strategy = Hexital(
            "Test Stratergy",
            candles[:100],
            [EMA(name="EMA"), SMA(name="SMA", timeframe="T5")],
        )
        strategy.calculate()

        found_candles = strategy.find_candle_pairing("high", "SMA")

        assert found_candles[0] == found_candles[1]
        assert (
            reading_by_candle(found_candles[0][-1], "SMA") is not None
            and reading_by_candle(found_candles[0][-1], "high")
            == strategy.candles("SMA")[-1].high
            and found_candles[0][-1].timeframe == timedelta(minutes=5)
        )

    def test_find_candles_multi_timeframes(self, candles):
        strategy = Hexital(
            "Test Stratergy",
            candles,
            [EMA(name="EMA_T5", timeframe="T5"), EMA(name="EMA")],
        )
        strategy.calculate()

        found_candles = strategy.find_candle_pairing("EMA", "EMA_T5")

        assert len(found_candles) == 2
        assert (
            reading_by_candle(found_candles[0][-1], "EMA") is not None
            and reading_by_candle(found_candles[0][-1], "high")
            == strategy.candles("EMA")[-1].high
        )
        assert found_candles[0][-1].timeframe == timedelta(seconds=60)

        assert (
            reading_by_candle(found_candles[1][-1], "EMA_T5") is not None
            and reading_by_candle(found_candles[1][-1], "high")
            == strategy.candles("EMA_T5")[-1].high
        )
        assert found_candles[1][-1].timeframe == timedelta(seconds=300)


class TestMultiTimeframesNames:
    def test_timeframe_default(self, candles_untimeframed):
        strategy = Hexital("Test Strategy", candles_untimeframed)
        assert [st.name for st in strategy._candle_managers] == ["DEFAULT"]

    def test_timeframe_multi(self, candles_untimeframed):
        strategy = Hexital("Test Strategy", candles_untimeframed, [EMA(timeframe="T1")])
        assert [st.name for st in strategy._candle_managers] == ["DEFAULT", "T1"]

    def test_duplicate_indicators(self, candles):
        strategy = Hexital(
            "Test Strategy", candles, [EMA(timeframe="T1"), SMA(timeframe="T1")]
        )
        assert [st.name for st in strategy._candle_managers] == ["DEFAULT", "T1"]

    def test_clash_hexital(self, candles):
        strategy = Hexital(
            "Test Strategy", candles, [EMA(timeframe="T1")], timeframe="T1"
        )
        assert [st.name for st in strategy._candle_managers] == ["T1"]

    def test_multi_hexital(self, candles):
        strategy = Hexital(
            "Test Strategy", candles, [EMA(timeframe="T5")], timeframe="T1"
        )
        assert [st.name for st in strategy._candle_managers] == ["T1", "T5"]


class TestHexitalSettings:
    def test_indicator_settings(self):
        strategy = Hexital("Test Strategy", [], [EMA(candles=[])])

        assert strategy.indicator_settings == [
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
        strategy = Hexital("Test Strategy", [], [EMA(candles=[]), Amorph(analysis=doji)])

        assert strategy.indicator_settings == [
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
        strategy = Hexital(
            "Test Strategy",
            [],
            [EMA(candles=[])],
            timeframe="T5",
            candle_life=timedelta(minutes=60),
        )

        assert strategy.settings == {
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
        strategy = Hexital(**as_dict)

        assert strategy.settings == as_dict


class TestIndicatorCollection:
    def test_collection(self, minimal_candles):
        @dataclass
        class customCol(IndicatorCollection):
            fake: Indicator = field(default_factory=FakeIndicator)

        collection = customCol()
        strategy = Hexital("collection", minimal_candles, collection)

        assert strategy.indicator("Fake_10")
        assert collection.fake.reading is not None

    def test_collectionRef(self, minimal_candles):
        @dataclass
        class customCol(IndicatorCollection):
            fake: Indicator = field(default_factory=FakeIndicator)

        strategy = HexitalCol("collection", minimal_candles, customCol())

        assert strategy.collection.fake
        assert strategy.collection.fake.reading is not None
