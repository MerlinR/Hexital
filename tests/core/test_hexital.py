from copy import deepcopy

import pytest
from hexital.core import Candle, Hexital
from hexital.exceptions import InvalidIndicator
from hexital.indicators import EMA, OBV, SMA


@pytest.mark.usefixtures("candles", "expected_ema")
def test_hextial_single(candles, expected_ema):
    strat = Hexital("Test Stratergy", candles)
    strat.add_indicator(EMA())
    strat.calculate()
    assert pytest.approx(strat.reading_as_list("EMA_10")) == expected_ema


@pytest.mark.usefixtures("candles", "expected_ema", "expected_sma")
def test_hextial_multi(candles, expected_ema, expected_sma):
    strat = Hexital("Test Stratergy", candles, [EMA(), SMA()])
    strat.calculate()
    assert (
        pytest.approx(strat.reading_as_list("EMA_10")) == expected_ema
        and pytest.approx(strat.reading_as_list("SMA_10")) == expected_sma
    )


@pytest.mark.usefixtures("candles", "expected_ema", "expected_sma")
def test_hextial_multi_dict(candles, expected_ema, expected_sma):
    strat = Hexital("Test Stratergy", candles, [EMA(), {"indicator": "SMA"}])
    strat.calculate()
    assert (
        pytest.approx(strat.reading_as_list("EMA_10")) == expected_ema
        and pytest.approx(strat.reading_as_list("SMA_10")) == expected_sma
    )


@pytest.mark.usefixtures("candles")
def test_hextial_multi_dict_invalid(candles):
    with pytest.raises(InvalidIndicator):
        Hexital("Test Stratergy", candles, [EMA(), {"indicator": "FUCK"}])


@pytest.mark.usefixtures("candles")
def test_hextial_multi_dict_invalid_missing(candles):
    with pytest.raises(InvalidIndicator):
        Hexital("Test Stratergy", candles, [{"period": 10}])


@pytest.mark.usefixtures("candles", "expected_ema", "expected_sma")
def test_hextial_multi_dict_append(candles, expected_ema, expected_sma):
    strat = Hexital("Test Stratergy", candles, [EMA()])
    strat.add_indicator({"indicator": "SMA"})
    strat.calculate()
    assert (
        pytest.approx(strat.reading_as_list("EMA_10")) == expected_ema
        and pytest.approx(strat.reading_as_list("SMA_10")) == expected_sma
    )


@pytest.mark.usefixtures("candles")
def test_hextial_dict_arguments(candles):
    strat = Hexital("Test Stratergy", candles, [{"indicator": "SMA", "period": 20}])
    assert strat.get_indicator("SMA_20")


@pytest.mark.usefixtures("candles", "expected_sma")
def test_hextial_read(candles, expected_sma):
    strat = Hexital("Test Stratergy", candles, [{"indicator": "SMA", "period": 10}])
    strat.calculate()
    assert pytest.approx(strat.reading("SMA")) == expected_sma[-1]


@pytest.mark.usefixtures("candles")
def test_hextial_reading(candles):
    strat = Hexital("Test Stratergy", candles, [{"indicator": "SMA", "period": 10}])
    assert strat.has_reading("SMA") is False

    strat.calculate()
    assert strat.has_reading("SMA")


@pytest.mark.usefixtures("candles")
def test_hextial_reading_exists_no_values(candles):
    strat = Hexital("Test Stratergy", candles, [{"indicator": "SMA", "period": 10}])
    assert strat.has_reading("SMA") is False


@pytest.mark.usefixtures("candles")
def test_hextial_reading_missing(candles):
    strat = Hexital("Test Stratergy", candles, [{"indicator": "SMA", "period": 10}])
    strat.calculate()
    assert strat.has_reading("EMA") is False


@pytest.mark.usefixtures("minimal_candles")
def test_hextial_append_candle(minimal_candles):
    new_candle = minimal_candles.pop(0)
    strat = Hexital("Test Stratergy", [])

    strat.append(new_candle)

    assert strat.candles == [new_candle]


@pytest.mark.usefixtures("minimal_candles")
def test_hextial_append_candle_list(minimal_candles):
    strat = Hexital("Test Stratergy", [])

    strat.append(minimal_candles)

    assert strat.candles == minimal_candles


def test_hextial_append_dict():
    strat = Hexital("Test Stratergy", [])

    strat.append(
        {
            "open": 17213,
            "high": 2395,
            "low": 7813,
            "close": 3615,
            "volume": 19661,
        }
    )
    assert strat.candles == [Candle(17213, 2395, 7813, 3615, 19661)]


@pytest.mark.usefixtures("candles")
def test_hextial_append_dict_list(candles):
    strat = Hexital("Test Stratergy", [])

    strat.append(
        [
            {
                "open": 17213,
                "high": 2395,
                "low": 7813,
                "close": 3615,
                "volume": 19661,
            },
            {
                "open": 1301,
                "high": 3007,
                "low": 11626,
                "close": 19048,
                "volume": 28909,
            },
        ]
    )

    assert strat.candles == [
        Candle(17213, 2395, 7813, 3615, 19661),
        Candle(1301, 3007, 11626, 19048, 28909),
    ]


def test_hextial_append_list():
    strat = Hexital("Test Stratergy", [])

    strat.append([17213, 2395, 7813, 3615, 19661])

    assert strat.candles == [Candle(17213, 2395, 7813, 3615, 19661)]


def test_hextial_append_list_list():
    strat = Hexital("Test Stratergy", [])

    strat.append(
        [
            [17213, 2395, 7813, 3615, 19661],
            [1301, 3007, 11626, 19048, 28909],
        ]
    )

    assert strat.candles == [
        Candle(17213, 2395, 7813, 3615, 19661),
        Candle(1301, 3007, 11626, 19048, 28909),
    ]


@pytest.mark.usefixtures("candles")
def test_hextial_append_invalid(candles):
    strat = Hexital("Test Stratergy", candles, [{"indicator": "SMA", "period": 10}])
    with pytest.raises(TypeError):
        strat.append(["Fuck", 2, 3])


@pytest.mark.usefixtures("candles", "expected_ema", "expected_sma")
def test_hextial_purge(candles, expected_ema, expected_sma):
    strat = Hexital("Test Stratergy", candles, [EMA(), {"indicator": "SMA"}])
    strat.calculate()

    assert strat.has_reading("SMA") and strat.has_reading("EMA")
    strat.purge("SMA_10")

    assert not strat.has_reading("SMA") and strat.has_reading("EMA")


@pytest.mark.usefixtures("candles", "expected_ema", "expected_sma")
def test_hextial_remove_indicator(candles, expected_ema, expected_sma):
    strat = Hexital("Test Stratergy", candles, [EMA(), {"indicator": "SMA"}])
    strat.calculate()

    assert strat.has_reading("SMA")

    strat.remove_indicator("SMA_10")

    assert not any(
        indicator for indicator in strat.indicators if indicator.name == "SMA_10"
    )


@pytest.mark.usefixtures("candles", "expected_ema", "expected_sma_t10")
def test_hextial_multi_timeframes(candles, expected_ema, expected_sma_t10):
    strat = Hexital("Test Stratergy", candles, [EMA(), SMA(timeframe="t10")])
    strat.calculate()
    assert pytest.approx(strat.reading_as_list("EMA_10")) == expected_ema
    assert pytest.approx(strat.reading_as_list("SMA_10_T10")) == expected_sma_t10


@pytest.mark.usefixtures("candles", "expected_ema", "expected_sma_t10")
def test_hextial_multi_timeframes_append(candles, expected_ema, expected_sma_t10):
    strat = Hexital("Test Stratergy", candles[:251], [EMA(), SMA(timeframe="t10")])
    strat.calculate()

    assert pytest.approx(strat.reading_as_list("EMA_10")) == expected_ema[:251]
    assert pytest.approx(strat.reading_as_list("SMA_10_T10")) == expected_sma_t10[:25]

    strat.append(candles[-249:])
    assert pytest.approx(strat.reading_as_list("EMA_10")) == expected_ema
    assert pytest.approx(strat.reading_as_list("SMA_10_T10")) == expected_sma_t10


@pytest.mark.usefixtures(
    "candles", "expected_ema", "expected_sma_t10", "expected_obv_t10"
)
def test_hextial_multi_timeframes_shared_candles(
    candles, expected_ema, expected_sma_t10, expected_obv_t10
):
    strat = Hexital(
        "Test Stratergy",
        candles,
        [EMA(), SMA(timeframe="t10"), {"indicator": "OBV", "timeframe": "T10"}],
    )
    strat.calculate()

    assert pytest.approx(strat.reading_as_list("EMA_10")) == expected_ema
    assert (
        strat._candles_timeframe["T10"][-1].indicators.get("SMA_10_T10")
        == expected_sma_t10[-1]
    )
    assert (
        strat._candles_timeframe["T10"][-1].indicators.get("OBV_T10")
        == expected_obv_t10[-1]
    )


# @pytest.mark.usefixtures("candles", "expected_sma_t10")
# def test_hextial_multi_timeframe_reading(candles, expected_sma_t10):
#     strat = Hexital("Test Stratergy", candles, [EMA(), SMA(timeframe="t10")])
#     strat.calculate()
#     assert pytest.approx(strat.reading("SMA_10_T10")) == expected_sma_t10[-1]
