import pytest
from hexital import indicators, patterns, movement
from hexital.core import Candle
from hexital.exceptions import InvalidPattern
from typing import List


def fake_pattern(candles: List[Candle], index=-1):
    return 1


@pytest.mark.usefixtures("candles")
def test_invalid_pattern(candles):
    with pytest.raises(InvalidPattern):
        indicators.Pattern(pattern="FUCK", candles=candles)


@pytest.mark.usefixtures("candles")
def test_string_pattern(candles):
    test = indicators.Pattern(pattern="doji", candles=candles)
    test.calculate()
    assert test.reading() is not None


@pytest.mark.usefixtures("candles")
def test_method_pattern(candles):
    test = indicators.Pattern(pattern=patterns.doji, candles=candles)
    test.calculate()
    assert test.reading() is not None


@pytest.mark.usefixtures("candles")
def test_pattern_multi_arguments(candles):
    test = indicators.Pattern(pattern=patterns.doji, candles=candles, length=20)
    test.calculate()
    assert test.name == "doji_20"


@pytest.mark.usefixtures("candles")
def test_pattern_dict_arguments(candles):
    test = indicators.Pattern(pattern=patterns.doji, candles=candles, args={"length": 20})
    test.calculate()
    assert test.name == "doji_20"


@pytest.mark.usefixtures("candles")
def test_pattern_merged_aguments(candles):
    test = indicators.Pattern(
        pattern=patterns.doji,
        candles=candles,
        length=20,
        fullname_override="MERGED_ARGS",
    )
    test.calculate()
    assert test.name == "MERGED_ARGS"


@pytest.mark.usefixtures("candles")
def test_string_movement(candles):
    test = indicators.Pattern(pattern="positive", candles=candles)
    test.calculate()
    assert test.reading("positive") is not None


@pytest.mark.usefixtures("candles")
def test_movement_pattern(candles):
    test = indicators.Pattern(pattern=movement.positive, candles=candles)
    test.calculate()
    assert test.reading("positive") is not None


@pytest.mark.usefixtures("candles")
def test_movement_pattern_args(candles):
    test = indicators.Pattern(
        pattern=movement.positive, candles=candles, fullname_override="boobies"
    )
    test.calculate()
    assert test.reading("boobies") is not None


@pytest.mark.usefixtures("candles")
def test_movement_pattern_kawgs(candles):
    test = indicators.Pattern(
        pattern=movement.above, candles=candles, indicator="open", indicator_two="low"
    )
    test.calculate()
    assert test.reading("above") is not None


@pytest.mark.usefixtures("candles")
def test_pattern_custom(candles):
    test = indicators.Pattern(pattern=fake_pattern, candles=candles)
    test.calculate()
    assert test.reading("fake_pattern") is not None
