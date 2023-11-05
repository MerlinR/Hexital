from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional

import pytest
from hexital.core import Candle, Indicator
from hexital.indicators.pattern import Pattern


@dataclass(kw_only=True)
class FakeIndicator(Indicator):
    candles: List[Candle] = field(default_factory=list)
    indicator_name: str = "Fake"
    fullname_override: Optional[str] = None
    name_suffix: Optional[str] = None
    round_value: int = 4
    
    period: int = 10
    input_value: str = "close"

    def _generate_name(self) -> str:
        return f"{self.indicator_name}_{self.period}"

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
    test = FakeIndicator(
        candles=minimal_candles, fullname_override="FUCK", name_suffix="YOU"
    )
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
    test = FakeIndicator(
        candles=minimal_candles, fullname_override="FUCK", timeframe="t5"
    )
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
    assert test.read is None
    test.calculate()
    assert test.read == 100.0


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
    assert test.read == 100
    test._set_reading(420)
    assert test.read == 420


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
        "indicator": "FakeIndicator",
        "round_value": 4,
        "indicator_name": "Fake",
        "input_value": "close",
        "period": 10,
    }


def test_settings_pattern():
    test = Pattern(pattern="doji")
    assert test.settings == {
        "pattern": "doji",
        "round_value": 4,
    }


@pytest.mark.usefixtures("minimal_candles")
def test_append_candle(minimal_candles):
    new_candle = minimal_candles.pop()
    new_candle.indicators["Fake_10"] = 100.0

    test = FakeIndicator(candles=[])
    test.append(new_candle)

    assert test.candles == [new_candle]


@pytest.mark.usefixtures("minimal_candles")
def test_append_candle_list(minimal_candles):
    test = FakeIndicator(candles=[])

    test.append(minimal_candles)

    for candle in minimal_candles:
        candle.indicators["Fake_10"] = 100.0

    assert test.candles == minimal_candles


def test_append_dict():
    test = FakeIndicator(candles=[])

    test.append(
        {
            "open": 17213,
            "high": 2395,
            "low": 7813,
            "close": 3615,
            "volume": 19661,
        }
    )
    assert test.candles == [
        Candle(17213, 2395, 7813, 3615, 19661, indicators={"Fake_10": 100.0})
    ]


def test_append_dict_list():
    test = FakeIndicator(candles=[])

    test.append(
        [
            {"open": 17213, "high": 2395, "low": 7813, "close": 3615, "volume": 19661},
            {"open": 1301, "high": 3007, "low": 11626, "close": 19048, "volume": 28909},
        ]
    )

    assert test.candles == [
        Candle(17213, 2395, 7813, 3615, 19661, indicators={"Fake_10": 100.0}),
        Candle(1301, 3007, 11626, 19048, 28909, indicators={"Fake_10": 100.0}),
    ]


def test_append_list():
    test = FakeIndicator(candles=[])

    test.append([17213, 2395, 7813, 3615, 19661])

    assert test.candles == [
        Candle(17213, 2395, 7813, 3615, 19661, indicators={"Fake_10": 100.0})
    ]


def test_append_list_list():
    test = FakeIndicator(candles=[])

    test.append([[17213, 2395, 7813, 3615, 19661], [1301, 3007, 11626, 19048, 28909]])

    assert test.candles == [
        Candle(17213, 2395, 7813, 3615, 19661, indicators={"Fake_10": 100.0}),
        Candle(1301, 3007, 11626, 19048, 28909, indicators={"Fake_10": 100.0}),
    ]


def test_append_invalid():
    test = FakeIndicator(candles=[])
    with pytest.raises(TypeError):
        test.append(["Fuck", 2, 3])


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
    test = FakeIndicator(candles=[], candles_timerange=timedelta(minutes=1))

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
