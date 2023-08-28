import pytest
from hexital.types.ohlcv import OHLCV
from hexital.utilities import (
    cross,
    crossover,
    crossunder,
    falling,
    highest,
    highestbar,
    lowest,
    lowestbar,
    mean_falling,
    mean_rising,
    negative,
    positive,
    rising,
)


@pytest.fixture(name="rising_candles")
def fixture_rising_candles():
    return [
        OHLCV(open=90, high=110, low=80, close=80, volume=10),
        OHLCV(open=100, high=120, low=90, close=90, volume=10),
        OHLCV(open=110, high=130, low=100, close=100, volume=10),
        OHLCV(open=120, high=140, low=110, close=110, volume=10),
        OHLCV(open=130, high=150, low=120, close=120, volume=10),
    ]


@pytest.fixture(name="fallling_candles")
def fixture_fallling_candles():
    return [
        OHLCV(open=130, high=150, low=120, close=120, volume=10),
        OHLCV(open=120, high=140, low=110, close=110, volume=10),
        OHLCV(open=110, high=130, low=100, close=100, volume=10),
        OHLCV(open=100, high=120, low=90, close=90, volume=10),
        OHLCV(open=90, high=110, low=80, close=80, volume=10),
    ]


@pytest.fixture(name="mixed_candles")
def fixture_mixed_candles():
    return [
        OHLCV(open=130, high=150, low=120, close=120, volume=10),
        OHLCV(open=120, high=140, low=110, close=110, volume=10),
        OHLCV(open=110, high=150, low=120, close=150, volume=10),
        OHLCV(open=150, high=120, low=90, close=110, volume=10),
        OHLCV(open=110, high=140, low=110, close=140, volume=10),
    ]


@pytest.fixture(name="mixed_candles_two")
def fixture_mixed_candles_two():
    return [
        OHLCV(open=130, high=150, low=120, close=120, volume=10),
        OHLCV(open=120, high=140, low=110, close=120, volume=10),
        OHLCV(open=110, high=150, low=120, close=130, volume=10),
        OHLCV(open=150, high=120, low=90, close=115, volume=10),
        OHLCV(open=115, high=140, low=110, close=120, volume=10),
    ]


@pytest.fixture(name="indicator_candles")
def fixture_indicator_candles():
    return [
        OHLCV(
            open=130, high=150, low=120, close=120, volume=10, indicators={"EMA_10": 100}
        ),
        OHLCV(
            open=120, high=140, low=110, close=120, volume=10, indicators={"EMA_10": 100}
        ),
        OHLCV(
            open=110, high=150, low=120, close=130, volume=10, indicators={"EMA_10": 100}
        ),
        OHLCV(
            open=150, high=120, low=90, close=115, volume=10, indicators={"EMA_10": 110}
        ),
        OHLCV(
            open=115, high=140, low=110, close=120, volume=10, indicators={"EMA_10": 140}
        ),
    ]


def test_positive():
    assert positive(OHLCV(open=100, high=120, low=90, close=110, volume=10))


def test_positive_false():
    assert not positive(OHLCV(open=100, high=120, low=90, close=90, volume=10))


def test_positive_list():
    assert not positive(
        [OHLCV(open=100, high=120, low=90, close=90, volume=10)], position=0
    )


def test_negative():
    assert negative(OHLCV(open=100, high=120, low=90, close=90, volume=10))


def test_negative_false():
    assert not negative(OHLCV(open=100, high=120, low=90, close=110, volume=10))


def test_negative_list():
    assert not negative(
        [OHLCV(open=100, high=120, low=90, close=110, volume=10)], position=0
    )


def test_basic_rising(rising_candles):
    assert rising(rising_candles, "close")


def test_basic_rising_false(fallling_candles):
    assert not rising(fallling_candles, "close")


def test_basic_falling(fallling_candles):
    assert falling(fallling_candles, "close")


def test_basic_falling_false(rising_candles):
    assert not falling(rising_candles, "close")


def test_mean_rising(mixed_candles):
    assert mean_rising(mixed_candles, "close")


def test_mean_rising_false(mixed_candles_two):
    assert not mean_rising(mixed_candles_two, "close")


def test_mean_falling(mixed_candles_two):
    assert mean_falling(mixed_candles_two, "close")


def test_mean_falling_false(mixed_candles):
    assert not mean_falling(mixed_candles, "close")


def test_highest(mixed_candles):
    assert highest(mixed_candles, "close") == 150


def test_highest_two(mixed_candles):
    assert highest(mixed_candles, "low") == 120


def test_lowest(mixed_candles_two):
    assert lowest(mixed_candles_two, "close") == 115


def test_lowest_two(mixed_candles_two):
    assert lowest(mixed_candles_two, "low") == 90


def test_highestbar(mixed_candles):
    assert highestbar(mixed_candles, "close") == 2


def test_highestbar_two(fallling_candles):
    assert highestbar(fallling_candles, "low") == 4


def test_lowestbars(mixed_candles_two):
    assert lowestbar(mixed_candles_two, "open") == 2


def test_lowestbars_two(mixed_candles_two):
    assert lowestbar(mixed_candles_two, "close") == 1


def test_lowestbars_two_length(mixed_candles_two):
    assert lowestbar(mixed_candles_two, "close", length=100) == 1


def test_cross(indicator_candles):
    assert cross(indicator_candles, "EMA_10", "close")


def test_cross_length(indicator_candles):
    assert cross(indicator_candles, "EMA_10", "close", length=100)


def test_cross_any_direction(indicator_candles):
    assert cross(indicator_candles, "close", "EMA_10")


def test_crossover(indicator_candles):
    assert crossover(indicator_candles, "EMA_10", "close")


def test_crossover_length(indicator_candles):
    assert crossover(indicator_candles, "EMA_10", "close", length=10)


def test_crossover_invalid(indicator_candles):
    assert crossover(indicator_candles, "close", "EMA_10") is False


def test_crosunder(indicator_candles):
    assert crossunder(indicator_candles, "close", "EMA_10")


def test_crosunder_length(indicator_candles):
    assert crossunder(indicator_candles, "close", "EMA_10", length=10)


def test_crosunder_invalid(indicator_candles):
    assert crossunder(indicator_candles, "EMA_10", "close") is False
