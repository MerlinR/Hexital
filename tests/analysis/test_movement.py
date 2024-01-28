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
        Candle(open=130, high=100, low=120, close=120, volume=10, indicators={"EMA_10": 100}),
        Candle(open=120, high=110, low=110, close=120, volume=10, indicators={"EMA_10": 100}),
        Candle(open=110, high=150, low=120, close=130, volume=10, indicators={"EMA_10": 100}),
        Candle(open=150, high=120, low=90, close=115, volume=10, indicators={"EMA_10": 110}),
        Candle(open=115, high=140, low=110, close=120, volume=10, indicators={"EMA_10": 140}),
    ]


@pytest.fixture(name="indicator_candles_partial")
def fixture_indicator_candles_partial():
    return [
        Candle(open=130, high=150, low=120, close=120, volume=10, indicators={}),
        Candle(open=120, high=140, low=110, close=120, volume=10, indicators={}),
        Candle(open=110, high=150, low=120, close=130, volume=10, indicators={"EMA_10": 100}),
        Candle(open=150, high=120, low=90, close=115, volume=10, indicators={"EMA_10": 110}),
        Candle(
            open=115,
            high=140,
            low=110,
            close=120,
            volume=10,
            indicators={"EMA_10": 140, "SMA_10": 100},
        ),
    ]


def test_positive_list():
    assert not movement.positive(
        [Candle(open=100, high=120, low=90, close=90, volume=10)], index=0
    )


def test_positive_list_missing():
    assert not movement.positive([])


def test_negative_list():
    assert not movement.negative(
        [Candle(open=100, high=120, low=90, close=110, volume=10)], index=0
    )


def test_negative_list_missing():
    assert not movement.negative([], index=0)


def test_negative_list_empty():
    assert not movement.negative([])


class TestAbove:
    def test_above(self, indicator_candles):
        assert movement.above(indicator_candles, "high", "low") is True

    def test_above_false(self, indicator_candles):
        assert movement.above(indicator_candles, "low", "high") is False

    def test_above_missing(self):
        assert movement.above([], "high", "low") is False

    def test_above_wrong(self, indicator_candles):
        assert movement.above(indicator_candles, "low", "high") is False

    def test_above_indicator(self, indicator_candles):
        assert movement.above(indicator_candles, "EMA_10", "close")

    def test_above_indicator_indexed(self, indicator_candles):
        assert movement.above(indicator_candles, "EMA_10", "close", -2) is False


class TestBelow:
    def test_below(self, indicator_candles):
        assert movement.below(indicator_candles, "high", "low") is False

    def test_below_false(self, indicator_candles):
        assert movement.below(indicator_candles, "low", "high") is True

    def test_below_missing(self):
        assert movement.below([], "high", "low") is False

    def test_below_wrong(self, indicator_candles):
        assert movement.below(indicator_candles, "low", "high")

    def test_below_indicator(self, indicator_candles):
        assert movement.below(indicator_candles, "EMA_10", "close") is False

    def test_below_indicator_indexed(self, indicator_candles):
        assert movement.below(indicator_candles, "EMA_10", "close", -2)


class TestValueRange:
    def test_value_range(self, rising_candles):
        assert movement.value_range(rising_candles, "close") == 40

    def test_value_range_missing(self):
        assert movement.value_range([], "close") is None

    def test_value_range_partial(self, indicator_candles_partial):
        assert movement.value_range(indicator_candles_partial, "EMA_10") == 40

    def test_value_range_prtial_missing(self, indicator_candles_partial):
        assert movement.value_range(indicator_candles_partial, "SMA_10") is None


class TestRising:
    def test_basic_rising(self, rising_candles):
        assert movement.rising(rising_candles, "close")

    def test_basic_rising_false(self, fallling_candles):
        assert movement.rising(fallling_candles, "close") is False

    def test_basic_rising_missing(self):
        assert movement.rising([], "close") is False

    def test_basic_rising_partial(self, indicator_candles_partial):
        assert movement.rising(indicator_candles_partial, "EMA_10") is True

    def test_basic_rising_partial_missing(self, indicator_candles_partial):
        assert movement.rising(indicator_candles_partial, "SMA_10") is False

    def test_basic_rising_length(self, rising_candles):
        assert movement.rising(rising_candles, "close", 100) is True


class TestFalling:
    def test_basic_falling(self, fallling_candles):
        assert movement.falling(fallling_candles, "close")

    def test_basic_falling_false(self, rising_candles):
        assert not movement.falling(rising_candles, "close")

    def test_basic_falling_missing(self):
        assert movement.falling([], "close") is False

    def test_basic_falling_partial(self, indicator_candles_partial):
        assert movement.falling(indicator_candles_partial, "EMA_10") is False

    def test_basic_falling_partial_missing(self, indicator_candles_partial):
        assert movement.falling(indicator_candles_partial, "SMA_10") is False

    def test_basic_falling_length(self, fallling_candles):
        assert movement.falling(fallling_candles, "close", 100) is True


class TestMeanRising:
    def test_mean_rising(self, mixed_candles):
        assert movement.mean_rising(mixed_candles, "close") is True

    def test_mean_rising_false(self, mixed_candles_two):
        assert movement.mean_rising(mixed_candles_two, "close") is False

    def test_mean_rising_empty(self):
        assert movement.mean_rising([], "close") is False

    def test_mean_rising_partial(self, indicator_candles_partial):
        assert movement.mean_rising(indicator_candles_partial, "EMA_10") is True

    def test_mean_rising_partial_missing(self, indicator_candles_partial):
        assert movement.mean_rising(indicator_candles_partial, "SMA_10") is False

    def test_mean_rising_length(self, mixed_candles):
        assert movement.mean_rising(mixed_candles, "close", 100) is True


class TestMeanFalling:
    def test_mean_falling(self, mixed_candles_two):
        assert movement.mean_falling(mixed_candles_two, "close")

    def test_mean_falling_false(self, mixed_candles):
        assert not movement.mean_falling(mixed_candles, "close")

    def test_mean_falling_empty(self):
        assert movement.mean_falling([], "close") is False

    def test_mean_falling_partial(self, indicator_candles_partial):
        assert movement.mean_falling(indicator_candles_partial, "EMA_10") is False

    def test_mean_falling_partial_missing(self, indicator_candles_partial):
        assert movement.mean_falling(indicator_candles_partial, "SMA_10") is False

    def test_mean_falling_length(self, mixed_candles):
        assert movement.mean_falling(mixed_candles, "close", 100) is False


class TestHighest:
    def test_highest(self, indicator_candles):
        assert movement.highest(indicator_candles, "close") == 130

    def test_highest_two(self, indicator_candles):
        assert movement.highest(indicator_candles, "low") == 120

    def test_highest_missing(self):
        assert movement.highest([], "close") is False

    def test_highest_partial(self, indicator_candles_partial):
        assert movement.highest(indicator_candles_partial, "EMA_10") == 140

    def test_highest_partial_missing(self, indicator_candles_partial):
        assert movement.highest(indicator_candles_partial, "SMA_10") == 100

    def test_highest_length(self, indicator_candles):
        assert movement.highest(indicator_candles, "open", 200) == 150


class TestLowest:
    def test_lowest(self, indicator_candles):
        assert movement.lowest(indicator_candles, "close") == 115

    def test_lowest_two(self, indicator_candles):
        assert movement.lowest(indicator_candles, "high") == 100

    def test_lowest_missing(self):
        assert movement.lowest([], "low") is False

    def test_lowest_partial(self, indicator_candles_partial):
        assert movement.lowest(indicator_candles_partial, "EMA_10") == 100

    def test_lowest_partial_missing(self, indicator_candles_partial):
        assert movement.lowest(indicator_candles_partial, "SMA_10") == 100

    def test_lowest_length(self, indicator_candles):
        assert movement.lowest(indicator_candles, "high", 100) == 100


class TestHighestBar:
    def test_highestbar(self, indicator_candles):
        assert movement.highestbar(indicator_candles, "close") == 2

    def test_highestbar_two(self, indicator_candles):
        assert movement.highestbar(indicator_candles, "low") == 2

    def test_highestbar_missing(self):
        assert movement.highestbar([], "close") is None

    def test_highestbar_partial(self, indicator_candles_partial):
        assert movement.highestbar(indicator_candles_partial, "EMA_10") == 0

    def test_highestbar_partial_missing(self, indicator_candles_partial):
        assert movement.highestbar(indicator_candles_partial, "SMA_10") == 0

    def test_highestbar_length(self, indicator_candles):
        assert movement.highestbar(indicator_candles, "low", 100) == 2


class TestLowestBar:
    def test_lowestbars(self, indicator_candles):
        assert movement.lowestbar(indicator_candles, "open") == 2

    def test_lowestbars_two(self, indicator_candles):
        assert movement.lowestbar(indicator_candles, "close") == 1

    def test_lowestbars_missing(self):
        assert movement.lowestbar([], "open") is None

    def test_lowestbars_partial(self, indicator_candles_partial):
        assert movement.lowestbar(indicator_candles_partial, "EMA_10") == 2

    def test_lowestbars_partial_missing(self, indicator_candles_partial):
        assert movement.lowestbar(indicator_candles_partial, "SMA_10") == 0

    def test_lowestbars_length(self, indicator_candles):
        assert movement.lowestbar(indicator_candles, "open", length=100) == 2


class TestCrossMethods:
    def test_cross(self, indicator_candles):
        assert movement.cross(indicator_candles, "EMA_10", "close") is True

    def test_cross_no_candles(self):
        assert movement.cross([], "EMA_10", "close") is False

    def test_cross_length(self, indicator_candles):
        assert movement.cross(indicator_candles, "EMA_10", "close", length=100) is True

    def test_cross_any_direction(self, indicator_candles):
        assert movement.cross(indicator_candles, "close", "EMA_10") is True

    def test_crossover(self, indicator_candles):
        assert movement.crossover(indicator_candles, "EMA_10", "close") is True

    def test_crossover_two(self, indicator_candles):
        assert movement.crossover(indicator_candles, "EMA_10", "low") is False

    def test_crossover_no_candles(self):
        assert movement.crossover([], "EMA_10", "close") is False

    def test_crossover_partial(self, indicator_candles_partial):
        assert movement.crossover(indicator_candles_partial, "volume", "EMA_10", 5) is False

    def test_crossover_partial_missing(self, indicator_candles_partial):
        assert movement.crossover(indicator_candles_partial, "volume", "SMA_10", 5) is False

    def test_crossover_length(self, indicator_candles):
        assert movement.crossover(indicator_candles, "EMA_10", "close", length=10) is True

    def test_crossunder(self, indicator_candles):
        assert movement.crossunder(indicator_candles, "close", "EMA_10") is True

    def test_crossunder_two(self, indicator_candles):
        assert movement.crossunder(indicator_candles, "low", "EMA_10") is False

    def test_crossunder_no_candles(self):
        assert movement.crossunder([], "close", "EMA_10") is False

    def test_crossunder_partial(self, indicator_candles_partial):
        assert movement.crossunder(indicator_candles_partial, "volume", "EMA_10", 5) is False

    def test_crossunder_partial_missing(self, indicator_candles_partial):
        assert movement.crossunder(indicator_candles_partial, "volume", "SMA_10", 5) is False

    def test_crossunder_length(self, indicator_candles):
        assert movement.crossunder(indicator_candles, "close", "EMA_10", length=10) is True
