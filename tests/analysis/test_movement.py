import pytest
from hexital.analysis import movement
from hexital.core.candle import Candle


@pytest.fixture(name="rising_candles")
def fixture_rising_candles():
    return [
        Candle(open=90, high=110, low=80, close=80, volume=10),
        Candle(open=100, high=120, low=90, close=90, volume=10),
        Candle(open=110, high=130, low=100, close=100, volume=10),
        Candle(open=120, high=140, low=110, close=110, volume=10),
        Candle(open=130, high=150, low=120, close=120, volume=10),
    ]


@pytest.fixture(name="fallling_candles")
def fixture_fallling_candles():
    return [
        Candle(open=130, high=150, low=120, close=120, volume=10),
        Candle(open=120, high=140, low=110, close=110, volume=10),
        Candle(open=110, high=130, low=100, close=100, volume=10),
        Candle(open=100, high=120, low=90, close=90, volume=10),
        Candle(open=90, high=110, low=80, close=80, volume=10),
    ]


@pytest.fixture(name="mixed_candles")
def fixture_mixed_candles():
    return [
        Candle(open=130, high=150, low=120, close=120, volume=10),
        Candle(open=120, high=140, low=110, close=110, volume=10),
        Candle(open=110, high=150, low=120, close=150, volume=10),
        Candle(open=150, high=120, low=90, close=110, volume=10),
        Candle(open=110, high=140, low=110, close=140, volume=10),
    ]


@pytest.fixture(name="mixed_candles_two")
def fixture_mixed_candles_two():
    return [
        Candle(open=130, high=150, low=120, close=120, volume=10),
        Candle(open=120, high=140, low=110, close=120, volume=10),
        Candle(open=110, high=150, low=120, close=130, volume=10),
        Candle(open=150, high=120, low=90, close=115, volume=10),
        Candle(open=115, high=140, low=110, close=120, volume=10),
    ]


@pytest.fixture(name="indicator_candles")
def fixture_indicator_candles():
    return [
        Candle(
            open=130, high=150, low=120, close=120, volume=10, indicators={"EMA_10": 100}
        ),
        Candle(
            open=120, high=140, low=110, close=120, volume=10, indicators={"EMA_10": 100}
        ),
        Candle(
            open=110, high=150, low=120, close=130, volume=10, indicators={"EMA_10": 100}
        ),
        Candle(
            open=150, high=120, low=90, close=115, volume=10, indicators={"EMA_10": 110}
        ),
        Candle(
            open=115, high=140, low=110, close=120, volume=10, indicators={"EMA_10": 140}
        ),
    ]


def test_positive():
    assert movement.positive(Candle(open=100, high=120, low=90, close=110, volume=10))


def test_positive_false():
    assert not movement.positive(Candle(open=100, high=120, low=90, close=90, volume=10))


def test_positive_list():
    assert not movement.positive(
        [Candle(open=100, high=120, low=90, close=90, volume=10)], position=0
    )


def test_negative():
    assert movement.negative(Candle(open=100, high=120, low=90, close=90, volume=10))


def test_negative_false():
    assert not movement.negative(Candle(open=100, high=120, low=90, close=110, volume=10))


def test_negative_list():
    assert not movement.negative(
        [Candle(open=100, high=120, low=90, close=110, volume=10)], position=0
    )


def test_value_range(rising_candles):
    assert movement.value_range(rising_candles, "close") == 40


def test_basic_rising(rising_candles):
    assert movement.rising(rising_candles, "close")


def test_basic_rising_false(fallling_candles):
    assert not movement.rising(fallling_candles, "close")


def test_basic_falling(fallling_candles):
    assert movement.falling(fallling_candles, "close")


def test_basic_falling_false(rising_candles):
    assert not movement.falling(rising_candles, "close")


def test_mean_rising(mixed_candles):
    assert movement.mean_rising(mixed_candles, "close")


def test_mean_rising_false(mixed_candles_two):
    assert not movement.mean_rising(mixed_candles_two, "close")


def test_mean_falling(mixed_candles_two):
    assert movement.mean_falling(mixed_candles_two, "close")


def test_mean_falling_false(mixed_candles):
    assert not movement.mean_falling(mixed_candles, "close")


def test_highest(mixed_candles):
    assert movement.highest(mixed_candles, "close") == 150


def test_highest_two(mixed_candles):
    assert movement.highest(mixed_candles, "low") == 120


def test_lowest(mixed_candles_two):
    assert movement.lowest(mixed_candles_two, "close") == 115


def test_lowest_two(mixed_candles_two):
    assert movement.lowest(mixed_candles_two, "low") == 90


def test_highestbar(mixed_candles):
    assert movement.highestbar(mixed_candles, "close") == 2


def test_highestbar_two(fallling_candles):
    assert movement.highestbar(fallling_candles, "low") == 4


def test_lowestbars(mixed_candles_two):
    assert movement.lowestbar(mixed_candles_two, "open") == 2


def test_lowestbars_two(mixed_candles_two):
    assert movement.lowestbar(mixed_candles_two, "close") == 1


def test_lowestbars_two_length(mixed_candles_two):
    assert movement.lowestbar(mixed_candles_two, "close", length=100) == 1


def test_cross(indicator_candles):
    assert movement.cross(indicator_candles, "EMA_10", "close")


def test_cross_length(indicator_candles):
    assert movement.cross(indicator_candles, "EMA_10", "close", length=100)


def test_cross_any_direction(indicator_candles):
    assert movement.cross(indicator_candles, "close", "EMA_10")


def test_crossover(indicator_candles):
    assert movement.crossover(indicator_candles, "EMA_10", "close")


def test_crossover_length(indicator_candles):
    assert movement.crossover(indicator_candles, "EMA_10", "close", length=10)


def test_crossover_invalid(indicator_candles):
    assert movement.crossover(indicator_candles, "close", "EMA_10") is False


def test_crosunder(indicator_candles):
    assert movement.crossunder(indicator_candles, "close", "EMA_10")


def test_crosunder_length(indicator_candles):
    assert movement.crossunder(indicator_candles, "close", "EMA_10", length=10)


def test_crosunder_invalid(indicator_candles):
    assert movement.crossunder(indicator_candles, "EMA_10", "close") is False
