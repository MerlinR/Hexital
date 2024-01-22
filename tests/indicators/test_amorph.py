import pytest
from hexital import patterns, movement
from hexital.indicators import Amorph
from hexital.core import Candle
from hexital.exceptions import InvalidAnalysis
from typing import List


def fake_pattern(candles: List[Candle], index=-1):
    return 1


@pytest.mark.usefixtures("candles")
def test_invalid_amorph(candles):
    with pytest.raises(InvalidAnalysis):
        Amorph(analysis="FUCK", candles=candles)


@pytest.mark.usefixtures("candles")
def test_string_amorph(candles):
    test = Amorph(analysis="doji", candles=candles)
    test.calculate()
    assert test.reading() is not None


@pytest.mark.usefixtures("candles")
def test_method_amorph(candles):
    test = Amorph(analysis=patterns.doji, candles=candles)
    test.calculate()
    assert test.reading() is not None


@pytest.mark.usefixtures("candles")
def test_amorph_multi_arguments(candles):
    test = Amorph(analysis=patterns.doji, candles=candles, length=20)
    test.calculate()
    assert test.name == "doji_20"


@pytest.mark.usefixtures("candles")
def test_amorph_dict_arguments(candles):
    test = Amorph(analysis=patterns.doji, candles=candles, args={"length": 20})
    test.calculate()
    assert test.name == "doji_20"


@pytest.mark.usefixtures("candles")
def test_amorph_merged_aguments(candles):
    test = Amorph(
        analysis=patterns.doji,
        candles=candles,
        length=20,
        fullname_override="MERGED_ARGS",
    )
    test.calculate()
    assert test.name == "MERGED_ARGS"


@pytest.mark.usefixtures("candles")
def test_string_movement(candles):
    test = Amorph(analysis="positive", candles=candles)
    test.calculate()
    assert test.reading("positive") is not None


@pytest.mark.usefixtures("candles")
def test_movement_amorph(candles):
    test = Amorph(analysis=movement.positive, candles=candles)
    test.calculate()
    assert test.reading("positive") is not None


@pytest.mark.usefixtures("candles")
def test_movement_amorph_args(candles):
    test = Amorph(analysis=movement.positive, candles=candles, fullname_override="boobies")
    test.calculate()
    assert test.reading("boobies") is not None


@pytest.mark.usefixtures("candles")
def test_movement_amorph_kawgs(candles):
    test = Amorph(analysis=movement.above, candles=candles, indicator="open", indicator_two="low")
    test.calculate()
    assert test.reading("above") is not None


@pytest.mark.usefixtures("candles")
def test_amorph_custom(candles):
    test = Amorph(analysis=fake_pattern, candles=candles)
    test.calculate()
    assert test.reading("fake_pattern") is not None
