from dataclasses import dataclass
from typing import List

import pytest
from hexital.core import Candle, Indicator


@dataclass(kw_only=True)
class SMA(Indicator):
    indicator_name: str = "SMA"
    period: int = 10
    input_value: str = "close"

    def _generate_name(self) -> str:
        return f"{self.indicator_name}_{self.period}"

    def _calculate_reading(self, index: int) -> float | dict | None:
        return 100.0


@pytest.mark.usefixtures("minimal_candles")
def test_calculate(minimal_candles: List[Candle]):
    test = SMA(candles=minimal_candles)
    test.calculate()
    assert minimal_candles[-1].indicators.get("SMA_10")


@pytest.mark.usefixtures("minimal_candles")
def test_name_default(minimal_candles: List[Candle]):
    test = SMA(candles=minimal_candles)
    test.calculate()
    assert test.reading("SMA_10")
    assert test.name == "SMA_10"


@pytest.mark.usefixtures("minimal_candles")
def test_name_fulloverride(minimal_candles: List[Candle]):
    test = SMA(candles=minimal_candles, fullname_override="FUCK")
    test.calculate()
    assert minimal_candles[-1].indicators.get("FUCK")


@pytest.mark.usefixtures("minimal_candles")
def test_name_fulloverride_and_suffix(minimal_candles: List[Candle]):
    test = SMA(candles=minimal_candles, fullname_override="FUCK", name_suffix="YOU")
    test.calculate()
    assert minimal_candles[-1].indicators.get("FUCK_YOU")


@pytest.mark.usefixtures("minimal_candles")
def test_name_suffix(minimal_candles: List[Candle]):
    test = SMA(candles=minimal_candles, name_suffix="YOU")
    test.calculate()
    assert minimal_candles[-1].indicators.get("SMA_10_YOU")


@pytest.mark.usefixtures("minimal_candles")
def test_read(minimal_candles: List[Candle]):
    test = SMA(candles=minimal_candles)
    assert test.read is None
    test.calculate()
    assert test.read == 100.0


@pytest.mark.usefixtures("minimal_candles")
def test_has_reading(minimal_candles: List[Candle]):
    test = SMA(candles=minimal_candles)
    assert test.has_reading is False
    test.calculate()
    assert test.has_reading is True


@pytest.mark.usefixtures("minimal_candles")
def test_set_reading(minimal_candles: List[Candle]):
    test = SMA(candles=minimal_candles)
    test.calculate()
    assert test.read == 100
    test._set_reading(420)
    assert test.read == 420


@pytest.mark.usefixtures("minimal_candles")
def test_set_reading_indexed(minimal_candles: List[Candle]):
    test = SMA(candles=minimal_candles)
    test.calculate()
    assert test.prev_reading() == 100
    test._set_reading(420, -2)
    assert test.prev_reading() == 420


@pytest.mark.usefixtures("minimal_candles")
def test_reading_period(minimal_candles: List[Candle]):
    test = SMA(candles=minimal_candles)
    assert test.reading_period(10) is False
    test.calculate()
    assert test.reading_period(10) is True


@pytest.mark.usefixtures("minimal_candles")
def test_append_candle(minimal_candles):
    new_candle = minimal_candles.pop()
    test = SMA(candles=[])

    test.append(new_candle)

    assert test.candles == [new_candle]


@pytest.mark.usefixtures("minimal_candles")
def test_append_candle_list(minimal_candles):
    test = SMA(candles=[])

    test.append(minimal_candles)

    assert test.candles == minimal_candles


def test_append_dict():
    test = SMA(candles=[])

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
        Candle(17213, 2395, 7813, 3615, 19661, indicators={"SMA_10": 100.0})
    ]


def test_append_dict_list():
    test = SMA(candles=[])

    test.append(
        [
            {"open": 17213, "high": 2395, "low": 7813, "close": 3615, "volume": 19661},
            {"open": 1301, "high": 3007, "low": 11626, "close": 19048, "volume": 28909},
        ]
    )

    assert test.candles == [
        Candle(17213, 2395, 7813, 3615, 19661, indicators={"SMA_10": 100.0}),
        Candle(1301, 3007, 11626, 19048, 28909, indicators={"SMA_10": 100.0}),
    ]


def test_append_list():
    test = SMA(candles=[])

    test.append([17213, 2395, 7813, 3615, 19661])

    assert test.candles == [
        Candle(17213, 2395, 7813, 3615, 19661, indicators={"SMA_10": 100.0})
    ]


def test_append_list_list():
    test = SMA(candles=[])

    test.append([[17213, 2395, 7813, 3615, 19661], [1301, 3007, 11626, 19048, 28909]])

    assert test.candles == [
        Candle(17213, 2395, 7813, 3615, 19661, indicators={"SMA_10": 100.0}),
        Candle(1301, 3007, 11626, 19048, 28909, indicators={"SMA_10": 100.0}),
    ]


def test_append_invalid():
    test = SMA(candles=[])
    with pytest.raises(TypeError):
        test.append(["Fuck", 2, 3])


@pytest.mark.usefixtures("minimal_candles")
def test_purge(minimal_candles: List[Candle]):
    test = SMA(candles=minimal_candles)
    assert test.has_reading is False
    test.calculate()
    assert test.has_reading is True
    test.purge()
    assert test.has_reading is False
