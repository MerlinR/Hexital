from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional

import pytest
from hexital import Candle
from hexital.analysis.patterns import doji
from hexital.candlesticks.heikinashi import HeikinAshi
from hexital.core.indicator import Indicator
from hexital.exceptions import InvalidCandlestickType
from hexital.indicators.amorph import Amorph


@dataclass(kw_only=True)
class FakeIndicator(Indicator):
    candles: List[Candle] = field(default_factory=list)
    _name: str = field(init=False, default="Fake")
    fullname_override: Optional[str] = None
    name_suffix: Optional[str] = None
    round_value: int = 4

    period: int = 10
    input_value: str = "close"

    def _generate_name(self) -> str:
        return f"{self._name}_{self.period}"

    def _calculate_reading(self, index: int) -> float | dict | None:
        return 100.0


@pytest.mark.usefixtures("minimal_candles")
def test_calculate(minimal_candles: List[Candle]):
    test = FakeIndicator(candles=minimal_candles)
    test.calculate()
    assert minimal_candles[-1].indicators.get("Fake_10")


@pytest.mark.usefixtures("minimal_candles")
def test_name_default(minimal_candles: List[Candle]):
    test = FakeIndicator(candles=minimal_candles)
    test.calculate()
    assert test.reading("Fake_10")
    assert test.name == "Fake_10"


@pytest.mark.usefixtures("minimal_candles")
def test_name_fulloverride(minimal_candles: List[Candle]):
    test = FakeIndicator(candles=minimal_candles, fullname_override="FUCK")
    test.calculate()
    assert test.name == "FUCK"


@pytest.mark.usefixtures("minimal_candles")
def test_name_fulloverride_and_suffix(minimal_candles: List[Candle]):
    test = FakeIndicator(candles=minimal_candles, fullname_override="FUCK", name_suffix="YOU")
    test.calculate()
    assert test.name == "FUCK_YOU"


@pytest.mark.usefixtures("minimal_candles")
def test_name_suffix(minimal_candles: List[Candle]):
    test = FakeIndicator(candles=minimal_candles, name_suffix="YOU")
    test.calculate()
    assert test.name == "Fake_10_YOU"


@pytest.mark.usefixtures("minimal_candles")
def test_name_timeframe(minimal_candles: List[Candle]):
    test = FakeIndicator(candles=minimal_candles, timeframe="t5")
    test.calculate()
    assert test.name == "Fake_10_T5"


@pytest.mark.usefixtures("minimal_candles")
def test_name_timeframe_override(minimal_candles: List[Candle]):
    test = FakeIndicator(candles=minimal_candles, fullname_override="FUCK", timeframe="t5")
    test.calculate()
    assert test.name == "FUCK"


@pytest.mark.usefixtures("minimal_candles")
def test_name_timeframe_suffix(minimal_candles: List[Candle]):
    test = FakeIndicator(candles=minimal_candles, name_suffix="YOU", timeframe="t5")
    test.calculate()
    assert test.name == "Fake_10_T5_YOU"


@pytest.mark.usefixtures("minimal_candles")
def test_read(minimal_candles: List[Candle]):
    test = FakeIndicator(candles=minimal_candles)
    assert test.reading() is None
    test.calculate()
    assert test.reading() == 100.0


@pytest.mark.usefixtures("minimal_candles")
def test_has_reading(minimal_candles: List[Candle]):
    test = FakeIndicator(candles=minimal_candles)
    assert test.has_reading is False
    test.calculate()
    assert test.has_reading is True


@pytest.mark.usefixtures("minimal_candles")
def test_set_reading(minimal_candles: List[Candle]):
    test = FakeIndicator(candles=minimal_candles)
    test.calculate()
    assert test.reading() == 100
    test._set_reading(420)
    assert test.reading() == 420


@pytest.mark.usefixtures("minimal_candles")
def test_set_reading_indexed(minimal_candles: List[Candle]):
    test = FakeIndicator(candles=minimal_candles)
    test.calculate()
    assert test.prev_reading() == 100
    test._set_reading(420, -2)
    assert test.prev_reading() == 420


@pytest.mark.usefixtures("minimal_candles")
def test_reading_period(minimal_candles: List[Candle]):
    test = FakeIndicator(candles=minimal_candles)
    assert test.reading_period(10) is False
    test.calculate()
    assert test.reading_period(10) is True


@pytest.mark.usefixtures("minimal_candles")
def test_settings(minimal_candles: List[Candle]):
    test = FakeIndicator(candles=minimal_candles)
    assert test.settings == {
        "indicator": "Fake",
        "round_value": 4,
        "input_value": "close",
        "period": 10,
    }


@pytest.mark.usefixtures("minimal_candles")
def test_settings_timeframe(minimal_candles: List[Candle]):
    test = FakeIndicator(candles=minimal_candles, timeframe="T5")
    assert test.settings == {
        "indicator": "Fake",
        "round_value": 4,
        "input_value": "close",
        "period": 10,
        "timeframe": "T5",
        "timeframe_fill": False,
    }


@pytest.mark.usefixtures("minimal_candles")
def test_settings_candlestick_types(minimal_candles: List[Candle]):
    test = FakeIndicator(candles=minimal_candles, candlestick_type="HA")
    assert test.settings == {
        "indicator": "Fake",
        "round_value": 4,
        "input_value": "close",
        "period": 10,
        "candlestick_type": "HA",
    }


def test_settings_analysis():
    test = Amorph(analysis=doji)
    assert test.settings == {
        "analysis": "doji",
        "round_value": 4,
    }


@pytest.mark.usefixtures("minimal_candles")
def test_purge(minimal_candles: List[Candle]):
    test = FakeIndicator(candles=minimal_candles)
    assert test.has_reading is False
    test.calculate()
    assert test.has_reading is True
    test.purge()
    assert test.has_reading is False


@pytest.mark.usefixtures("minimal_candles")
def test_candle_timerange(minimal_candles):
    test = FakeIndicator(candles=[], candles_lifespan=timedelta(minutes=1))

    test.append(minimal_candles)

    assert test.candles == [
        Candle(
            open=16346,
            high=4309,
            low=1903,
            close=6255,
            volume=31307,
            indicators={
                "ATR": 1900,
                "Fake_10": 100.0,
                "MinTR": 1902,
                "NATR": {"nested": 1901},
            },
            sub_indicators={"SATR": 1910, "SSATR": {"nested": 1911}},
            timestamp=datetime(2023, 6, 1, 9, 18),
        ),
        Candle(
            open=2424,
            high=10767,
            low=13115,
            close=13649,
            volume=15750,
            indicators={
                "ATR": 2000,
                "Fake_10": 100.0,
                "MinTR": 2002,
                "NATR": {"nested": 2001},
            },
            sub_indicators={"SATR": 2010, "SSATR": {"nested": 2011}},
            timestamp=datetime(2023, 6, 1, 9, 19),
        ),
    ]


@pytest.mark.usefixtures("minimal_candles")
def test_reading_as_list_exp(minimal_candles: List[Candle]):
    test_indicator = FakeIndicator(candles=minimal_candles)
    assert test_indicator.as_list("ATR") == [
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
    test_indicator = FakeIndicator(candles=minimal_candles)
    assert test_indicator.as_list("MinTR") == [
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
    test_indicator = FakeIndicator(candles=minimal_candles)
    assert test_indicator.as_list("FUCK") == [None] * 20


class TestCandlestickType:
    def test_indicator_candlestick_type(self):
        test_indicator = FakeIndicator(candles=[], candlestick_type=HeikinAshi())
        assert isinstance(test_indicator.candlestick_type, HeikinAshi)

    def test_indicator_candlestick_type_str(self):
        test_indicator = FakeIndicator(candles=[], candlestick_type="HA")
        assert isinstance(test_indicator.candlestick_type, HeikinAshi)

    def test_indicator_candlestick_type_error(self):
        with pytest.raises(InvalidCandlestickType):
            test_indicator = FakeIndicator(candles=[], candlestick_type="FUCK")
