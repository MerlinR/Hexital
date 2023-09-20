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


@pytest.mark.usefixtures("candles")
def test_calculate(candles: List[Candle]):
    test = SMA(candles=candles)
    test.calculate()
    assert candles[-1].indicators.get("SMA_10")


@pytest.mark.usefixtures("candles")
def test_name_default(candles: List[Candle]):
    test = SMA(candles=candles)
    test.calculate()
    assert test.reading("SMA_10")
    assert test.name == "SMA_10"


@pytest.mark.usefixtures("candles")
def test_name_fulloverride(candles: List[Candle]):
    test = SMA(candles=candles, fullname_override="FUCK")
    test.calculate()
    assert candles[-1].indicators.get("FUCK")


@pytest.mark.usefixtures("candles")
def test_name_fulloverride_and_suffix(candles: List[Candle]):
    test = SMA(candles=candles, fullname_override="FUCK", name_suffix="YOU")
    test.calculate()
    assert candles[-1].indicators.get("FUCK_YOU")


@pytest.mark.usefixtures("candles")
def test_name_suffix(candles: List[Candle]):
    test = SMA(candles=candles, name_suffix="YOU")
    test.calculate()
    assert candles[-1].indicators.get("SMA_10_YOU")


@pytest.mark.usefixtures("candles")
def test_read(candles: List[Candle]):
    test = SMA(candles=candles)
    assert test.read is None
    test.calculate()
    assert test.read == 100.0


@pytest.mark.usefixtures("candles")
def test_has_reading(candles: List[Candle]):
    test = SMA(candles=candles)
    assert test.has_reading is False
    test.calculate()
    assert test.has_reading is True


@pytest.mark.usefixtures("candles")
def test_reading_period(candles: List[Candle]):
    test = SMA(candles=candles)
    assert test.reading_period(10) is False
    test.calculate()
    assert test.reading_period(10) is True


@pytest.mark.usefixtures("candles")
def test_purge(candles: List[Candle]):
    test = SMA(candles=candles)
    assert test.has_reading is False
    test.calculate()
    assert test.has_reading is True
    test.purge()
    assert test.has_reading is False
