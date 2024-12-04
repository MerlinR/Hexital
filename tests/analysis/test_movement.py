from datetime import datetime, timedelta
from typing import List

import pytest
from hexital import Hexital
from hexital.analysis import movement
from hexital.core.candle import Candle
from hexital.indicators import EMA, Supertrend


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


@pytest.fixture(name="gen_ema")
def fixture_gen_ema(candles: List[Candle]):
    ema = EMA(candles=candles)
    ema.calculate()
    return ema.candles


@pytest.fixture(name="gen_indicator_candles")
def fixture_gen_indicator_candles(candles: List[Candle]):
    ema = EMA(name="EMA", candles=candles)
    ema.calculate()
    return ema


@pytest.fixture(name="hexital_candles")
def fixture_hexital_candles(candles: List[Candle]):
    strat = Hexital(
        "Multi-Timeframe",
        candles,
        [EMA(name="EMA")],
    )
    strat.calculate()
    return strat


@pytest.fixture(name="multi_candles")
def fixture_hexital_multi_candles(candles: List[Candle]):
    strat = Hexital(
        "Multi-Timeframe",
        candles,
        [EMA(name="EMA"), Supertrend(name="SUPERTREND")],
    )
    strat.calculate()
    return strat


@pytest.fixture(name="multi_timeframe_candles")
def fixture_hexital_multi_timeframe_candles(candles: List[Candle]):
    strat = Hexital(
        "Multi-Timeframe",
        candles,
        [EMA(name="EMA"), EMA(name="EMA_T5", timeframe="T5")],
    )
    strat.calculate()
    return strat


@pytest.fixture(name="multi_timeframe")
def fixture_hexital_multi_timeframe(candles: List[Candle]):
    strat = Hexital(
        "Multi-Timeframe",
        candles,
        [EMA(name="EMA", period=3), EMA(name="EMA_T5", timeframe="T5", period=10)],
    )
    strat.calculate()
    return strat


@pytest.fixture(name="indicator_candles")
def fixture_indicator_candles():
    return [
        Candle(
            open=130,
            high=100,
            low=120,
            close=120,
            volume=10,
            indicators={"EMA_10": 100, "dir": -1, "rising": True},
        ),
        Candle(
            open=120,
            high=110,
            low=110,
            close=120,
            volume=10,
            indicators={"EMA_10": 100, "dir": -1, "rising": True},
        ),
        Candle(
            open=110,
            high=150,
            low=120,
            close=130,
            volume=10,
            indicators={"EMA_10": 100, "dir": 1, "rising": True},
        ),
        Candle(
            open=150,
            high=120,
            low=90,
            close=115,
            volume=10,
            indicators={"EMA_10": 110, "dir": 1, "rising": True},
        ),
        Candle(
            open=115,
            high=140,
            low=110,
            close=120,
            volume=10,
            indicators={"EMA_10": 140, "dir": 1, "rising": False},
        ),
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
        assert movement.above(indicator_candles, "EMA_10", "close", index=-2) is False

    def test_above_datatype_indicator(self, gen_indicator_candles):
        assert movement.above(gen_indicator_candles, "EMA", "close") is True

    def test_above_datatype_hexital(self, hexital_candles):
        assert movement.above(hexital_candles, "EMA", "close") is True

    def test_above_datatype_hexital_rev(self, hexital_candles):
        assert movement.above(hexital_candles, "close", "EMA") is False

    def test_above_datatype_hexital_multi(self, multi_timeframe_candles):
        assert movement.above(multi_timeframe_candles, "EMA", "EMA_T5") is False

    def test_above_datatype_hexital_multi_rev(self, multi_timeframe_candles):
        assert movement.above(multi_timeframe_candles, "EMA_T5", "EMA") is True


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
        assert movement.below(indicator_candles, "EMA_10", "close", index=-2)

    def test_below_datatype_indicator(self, gen_indicator_candles):
        assert movement.below(gen_indicator_candles, "EMA", "close") is False

    def test_below_datatype_hexital(self, hexital_candles):
        assert movement.below(hexital_candles, "EMA", "close") is False

    def test_below_datatype_hexital_rev(self, hexital_candles):
        assert movement.below(hexital_candles, "close", "EMA") is True

    def test_below_datatype_hexital_multi(self, multi_timeframe_candles):
        assert movement.below(multi_timeframe_candles, "EMA", "EMA_T5") is True

    def test_below_datatype_hexital_multi_rev(self, multi_timeframe_candles):
        assert movement.below(multi_timeframe_candles, "EMA_T5", "EMA") is False


class TestValueRange:
    def test_value_range(self, rising_candles):
        assert movement.value_range(rising_candles, "close") == 30

    def test_value_range_missing(self):
        assert movement.value_range([], "close") is None

    def test_value_range_partial(self, indicator_candles_partial):
        assert movement.value_range(indicator_candles_partial, "EMA_10") == 40

    def test_value_range_partial_missing(self, indicator_candles_partial):
        assert movement.value_range(indicator_candles_partial, "SMA_10") is None


class TestRising:
    def test_basic_rising(self, rising_candles):
        assert movement.rising(rising_candles, "close") is True

    def test_basic_rising_false(self, fallling_candles):
        assert movement.rising(fallling_candles, "close") is False

    def test_basic_rising_missing(self):
        assert movement.rising([], "close") is False

    def test_basic_rising_partial(self, indicator_candles_partial):
        assert movement.rising(indicator_candles_partial, "EMA_10") is True

    def test_basic_rising_partial_missing(self, indicator_candles_partial):
        assert movement.rising(indicator_candles_partial, "SMA_10") is False

    def test_basic_rising_partial_missing_long(self, indicator_candles_partial):
        assert movement.rising(indicator_candles_partial, "SMA_10", length=4) is False

    def test_basic_rising_length(self, rising_candles):
        assert movement.rising(rising_candles, "close", 100) is True


class TestFalling:
    def test_basic_falling(self, fallling_candles):
        assert movement.falling(fallling_candles, "close") is True

    def test_basic_falling_false(self, rising_candles):
        assert movement.falling(rising_candles, "close") is False

    def test_basic_falling_missing(self):
        assert movement.falling([], "close") is False

    def test_basic_falling_partial(self, indicator_candles_partial):
        assert movement.falling(indicator_candles_partial, "EMA_10") is False

    def test_basic_falling_partial_missing(self, indicator_candles_partial):
        assert movement.falling(indicator_candles_partial, "SMA_10") is False

    def test_basic_falling_partial_missing_long(self, indicator_candles_partial):
        assert movement.falling(indicator_candles_partial, "SMA_10", length=4) is False

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
        assert movement.highest([], "close") is None

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
        assert movement.lowest(indicator_candles, "high") == 110

    def test_lowest_missing(self):
        assert movement.lowest([], "low") is None

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


class TestCross:
    def test_cross(self, indicator_candles):
        assert movement.cross(indicator_candles, "EMA_10", "close") is True

    def test_cross_no_candles(self):
        assert movement.cross([], "EMA_10", "close") is False

    def test_cross_length(self, indicator_candles):
        assert movement.cross(indicator_candles, "EMA_10", "close", length=100) is True

    def test_cross_any_direction(self, indicator_candles):
        assert movement.cross(indicator_candles, "close", "EMA_10") is True

    def test_cross_datatype_indicator(self, gen_indicator_candles):
        assert movement.cross(gen_indicator_candles, "EMA", "close") is False

    def test_cross_datatype_indicator_long(self, gen_indicator_candles):
        assert movement.cross(gen_indicator_candles, "EMA", "close", length=200) is True

    def test_cross_datatype_hexital(self, hexital_candles):
        assert movement.cross(hexital_candles, "EMA", "close") is False

    def test_cross_datatype_hexital_multi(self, multi_timeframe):
        assert movement.cross(multi_timeframe, "EMA", "EMA_T5") is False

    def test_cross_datatype_hexital_multi_long(self, multi_timeframe):
        assert movement.cross(multi_timeframe, "EMA", "EMA_T5", length=80) is True


class TestCrossOver:
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

    def test_crossover_datatype_indicator(self, gen_indicator_candles):
        assert movement.crossover(gen_indicator_candles, "EMA", "close") is False

    def test_crossover_datatype_indicator_long(self, gen_indicator_candles):
        assert movement.crossover(gen_indicator_candles, "EMA", "close", length=200) is True

    def test_crossover_datatype_hexital(self, hexital_candles):
        assert movement.crossover(hexital_candles, "EMA", "close") is False

    def test_crossover_datatype_hexital_multi(self, multi_timeframe):
        assert movement.crossover(multi_timeframe, "EMA", "EMA_T5") is False

    def test_crossover_datatype_hexital_multi_long(self, multi_timeframe):
        assert movement.crossover(multi_timeframe, "EMA", "EMA_T5", length=80) is True


class TestCrossUnder:
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

    def test_crossunder_datatype_indicator(self, gen_indicator_candles):
        assert movement.crossunder(gen_indicator_candles, "EMA", "close") is False

    def test_crossunder_datatype_indicator_long(self, gen_indicator_candles):
        assert movement.crossunder(gen_indicator_candles, "EMA", "close", length=200) is True

    def test_crossunder_datatype_hexital(self, hexital_candles):
        assert movement.crossunder(hexital_candles, "EMA", "close") is False

    def test_crossunder_datatype_hexital_multi(self, multi_timeframe):
        assert movement.crossunder(multi_timeframe, "EMA", "EMA_T5") is False

    def test_crossunder_datatype_hexital_multi_long(self, multi_timeframe):
        assert movement.crossunder(multi_timeframe, "EMA", "EMA_T5", length=80) is True


class TestFlipped:
    def test_flipped(self, indicator_candles):
        assert movement.flipped(indicator_candles, "dir") is False

    def test_flipped_length(self, indicator_candles):
        assert movement.flipped(indicator_candles, "dir", 8) is True

    def test_flipped_bool(self, indicator_candles):
        assert movement.flipped(indicator_candles, "rising") is True

    def test_flipped_index(self, indicator_candles):
        assert movement.flipped(indicator_candles, "rising", 1, -2) is False


class TestRetrieveCandles:
    def test_retrieve_candles_list(self, gen_ema):
        candles = movement._retrieve_candles(gen_ema)
        assert (
            isinstance(candles, list)
            and len(candles) == 1
            and len(candles[0]) > 1
            and isinstance(candles[0][0], Candle)
        )

    def test_retrieve_candles_indicator(self, gen_indicator_candles):
        candles = movement._retrieve_candles(gen_indicator_candles)
        assert (
            isinstance(candles, list)
            and len(candles) == 1
            and len(candles[0]) > 1
            and isinstance(candles[0][0], Candle)
        )

    def test_retrieve_candles_hexital_default(self, hexital_candles):
        candles = movement._retrieve_candles(hexital_candles)
        assert (
            isinstance(candles, list)
            and len(candles) == 1
            and len(candles[0]) > 1
            and isinstance(candles[0][0], Candle)
        )

    def test_retrieve_candles_hexital_single(self, multi_candles):
        candles = movement._retrieve_candles(multi_candles, "EMA")
        assert (
            isinstance(candles, list)
            and isinstance(candles[0], list) is True
            and len(candles[0]) > 0
            and len(candles[1]) == 0
        )

    def test_retrieve_candles_hexital_multi(self, multi_candles):
        candles = movement._retrieve_candles(multi_candles, "EMA", "SUPERTREND")
        assert (
            isinstance(candles, list)
            and isinstance(candles[0], list) is True
            and len(candles[0]) > 0
            and len(candles[1]) > 0
            and candles[0] == candles[1]
        )

    def test_retrieve_candles_hexital_multi_timeframe(self, multi_timeframe_candles):
        candles = movement._retrieve_candles(multi_timeframe_candles, "EMA", "EMA_T5")
        assert (
            isinstance(candles, list)
            and isinstance(candles[0], list) is True
            and len(candles[0]) > 0
            and len(candles[1]) > 0
            and "EMA" in candles[0][-1].indicators
            and "EMA_T5" not in candles[0][-1].indicators
            and "EMA" not in candles[1][-1].indicators
            and "EMA_T5" in candles[1][-1].indicators
        )


class TestTimeframePairCandles:
    def test_timeframe_pair_candles_same_timeframe(self, multi_candles):
        found_candles = movement._retrieve_candles(multi_candles, "EMA", "SUPERTREND")
        candles = movement._timeframe_pair_candles(found_candles)
        assert candles[0][0] == candles[1][0] and candles[0][-1] == candles[1][-1]

    def test_timeframe_pair_candles(self, multi_timeframe_candles):
        candles = movement._timeframe_pair_candles(
            movement._retrieve_candles(multi_timeframe_candles, "EMA", "EMA_T5")
        )
        expected = [
            [
                Candle(
                    open=14599.5,
                    high=14601.5,
                    low=14595.8,
                    close=14597.1,
                    volume=1370,
                    timeframe=None,
                    timestamp=datetime(2023, 10, 3, 17, 18),
                    indicators={"EMA": 14605.572},
                ),
                Candle(
                    open=14596.9,
                    high=14599.1,
                    low=14590.3,
                    close=14590.8,
                    volume=1095,
                    timeframe=None,
                    timestamp=datetime(2023, 10, 3, 17, 19),
                    indicators={"EMA": 14602.8862},
                ),
                Candle(
                    open=14590.6,
                    high=14592.6,
                    low=14586.3,
                    close=14588.6,
                    volume=1132,
                    timeframe=None,
                    timestamp=datetime(2023, 10, 3, 17, 20),
                    indicators={"EMA": 14600.2887},
                ),
                Candle(
                    open=14588.8,
                    high=14589.1,
                    low=14578.1,
                    close=14579.4,
                    volume=1601,
                    timeframe=None,
                    timestamp=datetime(2023, 10, 3, 17, 21),
                    indicators={"EMA": 14596.4908},
                ),
                Candle(
                    open=14579.5,
                    high=14583.1,
                    low=14578.0,
                    close=14579.1,
                    volume=859,
                    timeframe=None,
                    timestamp=datetime(2023, 10, 3, 17, 22),
                    indicators={"EMA": 14593.3288},
                ),
            ],
            [
                Candle(
                    open=14604.0,
                    high=14608.9,
                    low=14586.3,
                    close=14588.6,
                    volume=4799,
                    timeframe=timedelta(seconds=300),
                    timestamp=datetime(2023, 10, 3, 17, 20),
                    indicators={"EMA_T5": 14607.0035},
                ),
                Candle(
                    open=14604.0,
                    high=14608.9,
                    low=14586.3,
                    close=14588.6,
                    volume=4799,
                    timeframe=timedelta(seconds=300),
                    timestamp=datetime(2023, 10, 3, 17, 20),
                    indicators={"EMA_T5": 14607.0035},
                ),
                Candle(
                    open=14604.0,
                    high=14608.9,
                    low=14586.3,
                    close=14588.6,
                    volume=4799,
                    timeframe=timedelta(seconds=300),
                    timestamp=datetime(2023, 10, 3, 17, 20),
                    indicators={"EMA_T5": 14607.0035},
                ),
                Candle(
                    open=14588.8,
                    high=14589.1,
                    low=14578.0,
                    close=14579.1,
                    volume=2460,
                    timeframe=timedelta(seconds=300),
                    timestamp=datetime(2023, 10, 3, 17, 25),
                    indicators={"EMA_T5": 14601.9301},
                ),
                Candle(
                    open=14588.8,
                    high=14589.1,
                    low=14578.0,
                    close=14579.1,
                    volume=2460,
                    timeframe=timedelta(seconds=300),
                    timestamp=datetime(2023, 10, 3, 17, 25),
                    indicators={"EMA_T5": 14601.9301},
                ),
            ],
        ]

        expected[1][0].aggregation_factor = 5
        expected[1][1].aggregation_factor = 5
        expected[1][2].aggregation_factor = 5
        expected[1][3].aggregation_factor = 2
        expected[1][4].aggregation_factor = 2

        assert [candles[0][-5:], candles[1][-5:]] == expected

    def test_timeframe_pair_candles_flipped(self, multi_timeframe_candles):
        candles = movement._timeframe_pair_candles(
            movement._retrieve_candles(multi_timeframe_candles, "EMA_T5", "EMA")
        )
        expected = [
            [
                Candle(
                    open=14604.0,
                    high=14608.9,
                    low=14586.3,
                    close=14588.6,
                    volume=4799,
                    timeframe=timedelta(seconds=300),
                    timestamp=datetime(2023, 10, 3, 17, 20),
                    indicators={"EMA_T5": 14607.0035},
                ),
                Candle(
                    open=14588.8,
                    high=14589.1,
                    low=14578.0,
                    close=14579.1,
                    volume=2460,
                    timeframe=timedelta(seconds=300),
                    timestamp=datetime(2023, 10, 3, 17, 25),
                    indicators={"EMA_T5": 14601.9301},
                ),
            ],
            [
                Candle(
                    open=14590.6,
                    high=14592.6,
                    low=14586.3,
                    close=14588.6,
                    volume=1132,
                    timeframe=None,
                    timestamp=datetime(2023, 10, 3, 17, 20),
                    indicators={"EMA": 14600.2887},
                ),
                Candle(
                    open=14579.5,
                    high=14583.1,
                    low=14578.0,
                    close=14579.1,
                    volume=859,
                    timeframe=None,
                    timestamp=datetime(2023, 10, 3, 17, 22),
                    indicators={"EMA": 14593.3288},
                ),
            ],
        ]

        expected[0][0].aggregation_factor = 5
        expected[0][1].aggregation_factor = 2

        assert [candles[0][-2:], candles[1][-2:]] == expected

    def test_timeframe_pair_candles_length_diff(self, multi_timeframe_candles):
        found_candles = movement._retrieve_candles(multi_timeframe_candles, "EMA", "EMA_T5")
        found_candles[0] = found_candles[0][100:]
        candles = movement._timeframe_pair_candles(found_candles)
        expected = [
            [
                Candle(
                    open=14831.9,
                    high=14832.0,
                    low=14822.7,
                    close=14823.4,
                    volume=367,
                    timeframe=None,
                    timestamp=datetime(2023, 10, 3, 10, 42),
                    indicators={"EMA": 14835.575},
                    sub_indicators={},
                ),
                Candle(
                    open=14579.5,
                    high=14583.1,
                    low=14578.0,
                    close=14579.1,
                    volume=859,
                    timeframe=None,
                    timestamp=datetime(2023, 10, 3, 17, 22),
                    indicators={"EMA": 14593.3288},
                ),
            ],
            [
                Candle(
                    open=14836.0,
                    high=14836.1,
                    low=14816.5,
                    close=14818.2,
                    volume=1238,
                    timeframe=timedelta(seconds=300),
                    timestamp=datetime(2023, 10, 3, 10, 45),
                    indicators={"EMA_T5": 14832.4375},
                ),
                Candle(
                    open=14588.8,
                    high=14589.1,
                    low=14578.0,
                    close=14579.1,
                    volume=2460,
                    timeframe=timedelta(seconds=300),
                    timestamp=datetime(2023, 10, 3, 17, 25),
                    indicators={"EMA_T5": 14601.9301},
                ),
            ],
        ]
        expected[1][0].aggregation_factor = 5
        expected[1][1].aggregation_factor = 2
        assert [[candles[0][0], candles[0][-1]], [candles[1][0], candles[1][-1]]] == expected
