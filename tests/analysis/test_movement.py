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
            open=130, high=100, low=120, close=120, volume=10, indicators={"EMA_10": 100}
        ),
        Candle(
            open=120, high=110, low=110, close=120, volume=10, indicators={"EMA_10": 100}
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


@pytest.fixture(name="indicator_candles_partial")
def fixture_indicator_candles_partial():
    return [
        Candle(open=130, high=150, low=120, close=120, volume=10, indicators={}),
        Candle(open=120, high=140, low=110, close=120, volume=10, indicators={}),
        Candle(
            open=110, high=150, low=120, close=130, volume=10, indicators={"EMA_10": 100}
        ),
        Candle(
            open=150, high=120, low=90, close=115, volume=10, indicators={"EMA_10": 110}
        ),
        Candle(
            open=115,
            high=140,
            low=110,
            close=120,
            volume=10,
            indicators={"EMA_10": 140, "SMA_10": 100},
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


def test_positive_list_missing():
    assert not movement.positive([])


def test_negative():
    assert movement.negative(Candle(open=100, high=120, low=90, close=90, volume=10))


def test_negative_false():
    assert not movement.negative(Candle(open=100, high=120, low=90, close=110, volume=10))


def test_negative_list():
    assert not movement.negative(
        [Candle(open=100, high=120, low=90, close=110, volume=10)], position=0
    )


def test_negative_list_missing():
    assert not movement.negative([], position=0)


def test_negative_list_empty():
    assert not movement.negative([])


def test_value_range(rising_candles):
    assert movement.value_range(rising_candles, "close") == 40


def test_value_range_missing():
    assert movement.value_range([], "close") is None


def test_value_range_partial(indicator_candles_partial):
    assert movement.value_range(indicator_candles_partial, "EMA_10") == 40


def test_value_range_prtial_missing(indicator_candles_partial):
    assert movement.value_range(indicator_candles_partial, "SMA_10") is None


def test_basic_rising(rising_candles):
    assert movement.rising(rising_candles, "close")


def test_basic_rising_false(fallling_candles):
    assert movement.rising(fallling_candles, "close") is False


def test_basic_rising_missing():
    assert movement.rising([], "close") is False


def test_basic_rising_partial(indicator_candles_partial):
    assert movement.rising(indicator_candles_partial, "EMA_10") is True


def test_basic_rising_partial_missing(indicator_candles_partial):
    assert movement.rising(indicator_candles_partial, "SMA_10") is False


def test_basic_rising_length(rising_candles):
    assert movement.rising(rising_candles, "close", 100) is True


def test_basic_falling(fallling_candles):
    assert movement.falling(fallling_candles, "close")


def test_basic_falling_false(rising_candles):
    assert not movement.falling(rising_candles, "close")


def test_basic_falling_missing():
    assert movement.falling([], "close") is False


def test_basic_falling_partial(indicator_candles_partial):
    assert movement.falling(indicator_candles_partial, "EMA_10") is False


def test_basic_falling_partial_missing(indicator_candles_partial):
    assert movement.falling(indicator_candles_partial, "SMA_10") is False


def test_basic_falling_length(fallling_candles):
    assert movement.falling(fallling_candles, "close", 100) is True


def test_mean_rising(mixed_candles):
    assert movement.mean_rising(mixed_candles, "close") is True


def test_mean_rising_false(mixed_candles_two):
    assert movement.mean_rising(mixed_candles_two, "close") is False


def test_mean_rising_empty():
    assert movement.mean_rising([], "close") is False


def test_mean_rising_partial(indicator_candles_partial):
    assert movement.mean_rising(indicator_candles_partial, "EMA_10") is True


def test_mean_rising_partial_missing(indicator_candles_partial):
    assert movement.mean_rising(indicator_candles_partial, "SMA_10") is False


def test_mean_rising_length(mixed_candles):
    assert movement.mean_rising(mixed_candles, "close", 100) is True


def test_mean_falling(mixed_candles_two):
    assert movement.mean_falling(mixed_candles_two, "close")


def test_mean_falling_false(mixed_candles):
    assert not movement.mean_falling(mixed_candles, "close")


def test_highest(indicator_candles):
    assert movement.highest(indicator_candles, "close") == 130


def test_highest_two(indicator_candles):
    assert movement.highest(indicator_candles, "low") == 120


def test_highest_missing():
    assert movement.highest([], "close") is False


def test_highest_partial(indicator_candles_partial):
    assert movement.highest(indicator_candles_partial, "EMA_10") == 140


def test_highest_partial_missing(indicator_candles_partial):
    assert movement.highest(indicator_candles_partial, "SMA_10") == 100


def test_highest_length(indicator_candles):
    assert movement.highest(indicator_candles, "open", 200) == 150


def test_lowest(indicator_candles):
    assert movement.lowest(indicator_candles, "close") == 115


def test_lowest_two(indicator_candles):
    assert movement.lowest(indicator_candles, "high") == 110


def test_lowest_missing():
    assert movement.lowest([], "low") is False


def test_lowest_partial(indicator_candles_partial):
    assert movement.lowest(indicator_candles_partial, "EMA_10") == 100


def test_lowest_partial_missing(indicator_candles_partial):
    assert movement.lowest(indicator_candles_partial, "SMA_10") == 100


def test_lowest_length(indicator_candles):
    assert movement.lowest(indicator_candles, "high", 100) == 100


def test_highestbar(indicator_candles):
    assert movement.highestbar(indicator_candles, "close") == 2


def test_highestbar_two(indicator_candles):
    assert movement.highestbar(indicator_candles, "low") == 2


def test_highestbar_missing():
    assert movement.highestbar([], "close") is None


def test_highestbar_partial(indicator_candles_partial):
    assert movement.highestbar(indicator_candles_partial, "EMA_10") == 0


def test_highestbar_partial_missing(indicator_candles_partial):
    assert movement.highestbar(indicator_candles_partial, "SMA_10") == 0


def test_highestbar_length(indicator_candles):
    assert movement.highestbar(indicator_candles, "low", 100) == 2


def test_lowestbars(indicator_candles):
    assert movement.lowestbar(indicator_candles, "open") == 2


def test_lowestbars_two(indicator_candles):
    assert movement.lowestbar(indicator_candles, "close") == 1


def test_lowestbars_missing():
    assert movement.lowestbar([], "open") is None


def test_lowestbars_partial(indicator_candles_partial):
    assert movement.lowestbar(indicator_candles_partial, "EMA_10") == 2


def test_lowestbars_partial_missing(indicator_candles_partial):
    assert movement.lowestbar(indicator_candles_partial, "SMA_10") == 0


def test_lowestbars_length(indicator_candles):
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
        assert (
            movement.crossover(indicator_candles_partial, "volume", "EMA_10", 5) is False
        )

    def test_crossover_partial_missing(self, indicator_candles_partial):
        assert (
            movement.crossover(indicator_candles_partial, "volume", "SMA_10", 5) is False
        )

    def test_crossover_length(self, indicator_candles):
        assert movement.crossover(indicator_candles, "EMA_10", "close", length=10) is True

    def test_crossunder(self, indicator_candles):
        assert movement.crossunder(indicator_candles, "close", "EMA_10") is True

    def test_crossunder_two(self, indicator_candles):
        assert movement.crossunder(indicator_candles, "low", "EMA_10") is False

    def test_crossunder_no_candles(self):
        assert movement.crossunder([], "close", "EMA_10") is False

    def test_crossunder_partial(self, indicator_candles_partial):
        assert (
            movement.crossunder(indicator_candles_partial, "volume", "EMA_10", 5) is False
        )

    def test_crossunder_partial_missing(self, indicator_candles_partial):
        assert (
            movement.crossunder(indicator_candles_partial, "volume", "SMA_10", 5) is False
        )

    def test_crossunder_length(self, indicator_candles):
        assert (
            movement.crossunder(indicator_candles, "close", "EMA_10", length=10) is True
        )
