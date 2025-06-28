from typing import List

import pytest
from hexital.core.candle import Candle
from hexital.core.candlestick_type import CandlestickType
from hexital.utils.common import CalcMode


class FakeType(CandlestickType):
    name: str = "Fake_Type"
    acronym: str = "Fake_Type"

    def transform_candle(self, candle: Candle) -> None | Candle | List[Candle]:
        candle = candle.clean_copy()
        candle.open = candle.open + 100
        candle.high = candle.high + 100
        candle.low = candle.low + 100
        candle.close = candle.close + 100
        return candle


class FakeJumpyType(CandlestickType):
    """Testing Candlesticks, to test No Candle being generated, and mulitple. will create a new Candle when volume changes 100, None if not by 100, and multiple (one per 100)"""

    name: str = "Fake_Jumpy_Type"
    acronym: str = "Fake_Jumpy_Type"
    vol_jump = 100

    def transform_candle(self, candle: Candle) -> None | Candle | List[Candle]:
        prev_derived = self.prev_derived()

        candles = None
        if not prev_derived:
            candles = candle.clean_copy()
            candles.timestamp = None
        elif abs(prev_derived.volume - candle.volume) == 100:
            candles = candle.clean_copy()
            candles.timestamp = None
        elif abs(prev_derived.volume - candle.volume) > 100:
            diff = abs(prev_derived.volume - candle.volume)
            count = int(diff / 100)
            candles = []
            c = prev_derived

            for _ in range(count):
                c = c.clean_copy()
                c.timestamp = None
                c.volume += 100
                candles.append(c)

        return candles


@pytest.mark.usefixtures("candles")
def test_naming(candles: List[Candle]):
    faketype = FakeType()
    faketype.set_candle_refs(candles)
    faketype.transform(CalcMode.APPEND)

    for candle in faketype.derived_candles:
        assert faketype.acronym == candle.tag


@pytest.mark.usefixtures("minimal_candles", "candles_candlesticks")
def test_conversion(minimal_candles: List[Candle], candles_candlesticks: List[Candle]):
    faketype = FakeType()
    faketype.set_candle_refs(minimal_candles)
    faketype.transform(CalcMode.APPEND)

    assert faketype.derived_candles == candles_candlesticks


@pytest.mark.usefixtures("minimal_candles", "candles_candlesticks")
def test_conv_redone(minimal_candles: List[Candle], candles_candlesticks: List[Candle]):
    faketype = FakeType()
    faketype.set_candle_refs(minimal_candles)
    faketype.transform(CalcMode.APPEND)
    faketype.transform(CalcMode.APPEND)

    assert faketype.derived_candles == candles_candlesticks


@pytest.mark.usefixtures("minimal_candles", "candles_candlesticks")
def test_conv_append(minimal_candles: List[Candle], candles_candlesticks: List[Candle]):
    faketype = FakeType()
    faketype.set_candle_refs(minimal_candles[:-1])
    faketype.transform(CalcMode.APPEND)

    faketype.candles.append(minimal_candles[-1])
    faketype.transform(CalcMode.APPEND)

    assert faketype.derived_candles == candles_candlesticks


@pytest.mark.usefixtures("minimal_candles", "candles_candlesticks")
def test_conv_append_bulk(minimal_candles: List[Candle], candles_candlesticks: List[Candle]):
    faketype = FakeType()

    for candle in minimal_candles:
        faketype.candles.append(candle)
        faketype.transform(CalcMode.APPEND)

    assert faketype.derived_candles == candles_candlesticks


@pytest.mark.usefixtures("minimal_candles", "candles_candlesticks")
def test_conv_preappend(minimal_candles: List[Candle], candles_candlesticks: List[Candle]):
    faketype = FakeType()
    faketype.set_candle_refs(minimal_candles[1:])

    faketype.transform(CalcMode.PREPEND)
    faketype.candles.insert(0, minimal_candles[0])
    faketype.transform(CalcMode.PREPEND)

    assert faketype.derived_candles == candles_candlesticks


@pytest.mark.usefixtures("minimal_candles", "candles_candlesticks")
def test_conv_preappend_bulk(minimal_candles: List[Candle], candles_candlesticks: List[Candle]):
    faketype = FakeType()

    for candle in reversed(minimal_candles):
        faketype.candles.insert(0, candle)
        faketype.transform(CalcMode.PREPEND)

    assert faketype.derived_candles == candles_candlesticks


@pytest.mark.usefixtures("minimal_candles", "candles_candlesticks")
def test_conv_insert(minimal_candles: List[Candle], candles_candlesticks: List[Candle]):
    faketype = FakeType()
    faketype.set_candle_refs(minimal_candles[:9] + minimal_candles[10:])
    faketype.transform(CalcMode.APPEND)

    faketype.candles.insert(9, minimal_candles[9])
    faketype.transform(CalcMode.INSERT)

    assert faketype.derived_candles == candles_candlesticks


@pytest.mark.usefixtures("minimal_candles", "candles_candlesticks")
def test_conv_insert_bulk(minimal_candles: List[Candle], candles_candlesticks: List[Candle]):
    faketype = FakeType()

    for candle in reversed(minimal_candles):
        faketype.candles.insert(0, candle)
        faketype.transform(CalcMode.INSERT)

    assert faketype.derived_candles == candles_candlesticks


@pytest.mark.usefixtures("minimal_candles_jumpy", "minimal_candles_jumpy_exp")
def test_conv_sticks_none_values(
    minimal_candles_jumpy: List[Candle], minimal_candles_jumpy_exp: List[Candle]
):
    faketype = FakeJumpyType()
    faketype.set_candle_refs(minimal_candles_jumpy[:5])

    faketype.transform(CalcMode.APPEND)
    assert faketype.derived_candles == minimal_candles_jumpy_exp[:4]


@pytest.mark.usefixtures("minimal_candles_jumpy", "minimal_candles_jumpy_exp")
def test_conv_sticks_jump_values(
    minimal_candles_jumpy: List[Candle], minimal_candles_jumpy_exp: List[Candle]
):
    faketype = FakeJumpyType()
    faketype.set_candle_refs(minimal_candles_jumpy[-5:])

    faketype.transform(CalcMode.APPEND)
    assert faketype.derived_candles == minimal_candles_jumpy_exp[-6:]


@pytest.mark.usefixtures("minimal_candles_jumpy", "minimal_candles_jumpy_exp")
def test_conv_sticks_mix_values(
    minimal_candles_jumpy: List[Candle], minimal_candles_jumpy_exp: List[Candle]
):
    faketype = FakeJumpyType()
    faketype.set_candle_refs(minimal_candles_jumpy)
    faketype.transform(CalcMode.APPEND)

    assert faketype.derived_candles == minimal_candles_jumpy_exp


@pytest.mark.usefixtures("minimal_candles_jumpy", "minimal_candles_jumpy_exp")
def test_conv_sticks_mix_append(
    minimal_candles_jumpy: List[Candle], minimal_candles_jumpy_exp: List[Candle]
):
    faketype = FakeJumpyType()

    for candle in minimal_candles_jumpy:
        faketype.candles.append(candle)
        faketype.transform(CalcMode.APPEND)

    assert faketype.derived_candles == minimal_candles_jumpy_exp
