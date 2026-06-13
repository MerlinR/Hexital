from datetime import timedelta

import pytest
from hexital.candlesticks.heikinashi import HeikinAshi
from hexital.core.hexital import Hexital
from hexital.indicators import EMA, OBV, SMA
from hexital.utils.timeframe import NullTimeFrame


def test_hextial_multi_timeframes(candles, expected_ema, expected_sma_t10):
    strategy = Hexital("Test Strategy", candles, [EMA(), SMA(timeframe="t10")])
    strategy.calculate()
    assert pytest.approx(strategy.reading_as_list("EMA_10")) == expected_ema
    assert pytest.approx(strategy.reading_as_list("SMA_10_T10")) == expected_sma_t10


def test_hextial_multi_timeframes_append(candles, expected_ema, expected_sma_t10):
    strategy = Hexital("Test Strategy", candles[:251], [EMA(), SMA(timeframe="t10")])
    strategy.calculate()

    assert pytest.approx(strategy.reading_as_list("EMA_10")) == expected_ema[:251]
    assert (
        pytest.approx(strategy.reading_as_list("SMA_10_T10"), 1.5e-1)
        == expected_sma_t10[:26]
    )

    strategy.append(candles[-249:])

    assert pytest.approx(strategy.reading_as_list("EMA_10")) == expected_ema
    assert pytest.approx(strategy.reading_as_list("SMA_10_T10")) == expected_sma_t10


def test_hextial_multi_timeframes_shared_candles(
    candles, expected_ema, expected_sma_t10, expected_obv_t10
):
    strategy = Hexital(
        "Test Strategy",
        candles,
        [EMA(), SMA(timeframe="t10"), {"indicator": "OBV", "timeframe": "T10"}],
    )
    strategy.calculate()

    candles_name = None
    for st in strategy._candle_managers:
        if st.name != NullTimeFrame.name:
            candles_name = st.name

    if not candles_name:
        assert False

    assert len(strategy._candle_managers) == 2
    assert pytest.approx(strategy.reading_as_list("EMA_10")) == expected_ema
    assert (
        strategy.candles(candles_name)[-1].indicators.get("SMA_10_T10")
        == expected_sma_t10[-1]
        and strategy.candles(candles_name)[-1].indicators.get("OBV_T10")
        == expected_obv_t10[-1]
    )


def test_hextial_multi_timeframes_get_candles(candles):
    strategy = Hexital(
        "Test Strategy",
        candles,
        [SMA(timeframe="t10"), OBV(timeframe="T10")],
    )
    strategy.calculate()

    candles_name = None
    for st in strategy._candle_managers:
        if st.name != NullTimeFrame.name:
            candles_name = st.name

    assert strategy.candles(candles_name)[-1].indicators.get(
        "SMA_10_T10"
    ) and strategy.candles(candles_name)[-1].indicators.get("OBV_T10")


def test_hextial_multi_timeframe_reading(candles, expected_sma_t10):
    strategy = Hexital("Test Strategy", candles, [EMA(), SMA(timeframe="t10")])
    strategy.calculate()
    assert pytest.approx(strategy.reading("SMA_10_T10")) == expected_sma_t10[-1]


def test_hextial_multi_timeframes_lifespan(candles, expected_ema, expected_sma_t5):
    strategy = Hexital(
        "Test Strategy",
        [],
        [EMA(), SMA(timeframe="t5")],
        candle_life=timedelta(hours=1),
    )

    for candle in candles:
        strategy.append(candle)

    assert pytest.approx(strategy.reading_as_list("EMA_10")) == expected_ema[-61:]
    assert (
        pytest.approx(strategy.reading_as_list("SMA_10_T5"), 1.5e-02)
        == expected_sma_t5[-13:]
    )


def test_hextial_multi_timeframes_candlesticks(candles):
    strategy = Hexital(
        "Test Strategy", candles, [EMA(timeframe="t5", candlestick=HeikinAshi())]
    )
    strategy.calculate()

    assert (
        isinstance(strategy.indicators["EMA_10_T5_HA"].candlestick, HeikinAshi)
        and strategy.indicators["EMA_10_T5_HA"].candles[-1].tag == "HA"
    )
