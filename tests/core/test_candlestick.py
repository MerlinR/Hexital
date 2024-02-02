from typing import List

import pytest
from hexital.core.candle import Candle
from hexital.core.candlestick_type import CandlestickType


class FakeType(CandlestickType):
    name: str = "Fake_Type"

    def convert_candle(self, candle: Candle, candles: List[Candle], index: int):
        candle.open = candle.open + 100
        candle.high = candle.high + 100
        candle.low = candle.low + 100
        candle.close = candle.close + 100


@pytest.mark.usefixtures("candles")
def test_naming(candles: List[Candle]):
    faketype = FakeType()
    faketype.conversion(candles)

    for candle in candles:
        assert candle.tag == faketype.name


@pytest.mark.usefixtures("minimal_candles")
def test_find_start_index_none(minimal_candles):
    faketype = FakeType()

    assert faketype._find_conv_index(minimal_candles) == 0


@pytest.mark.usefixtures("minimal_candles")
def test_find_start_index_half(minimal_candles):
    faketype = FakeType()
    minimal_candles[0].tag = "Fake_Type"
    minimal_candles[1].tag = "Fake_Type"

    assert faketype._find_conv_index(minimal_candles) == 2


@pytest.mark.usefixtures("minimal_candles")
def test_find_start_index_all(minimal_candles):
    faketype = FakeType()
    minimal_candles[0].tag = "Fake_Type"
    minimal_candles[-1].tag = "Fake_Type"

    assert faketype._find_conv_index(minimal_candles) == 20


@pytest.mark.usefixtures("minimal_candles", "minimal_conv_candles_exp")
def test_conversion(minimal_candles: List[Candle], minimal_conv_candles_exp: List[Candle]):
    faketype = FakeType()
    faketype.conversion(minimal_candles)

    assert minimal_candles == minimal_conv_candles_exp
