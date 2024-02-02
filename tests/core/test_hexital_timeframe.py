from datetime import timedelta

import pytest
from hexital.core.hexital import DEFAULT_CANDLES, Hexital
from hexital.indicators import EMA, OBV, SMA


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
    assert pytest.approx(strat.reading_as_list("SMA_10_T10"), 1.5e-1) == expected_sma_t10[:26]

    strat.append(candles[-249:])
    assert pytest.approx(strat.reading_as_list("EMA_10")) == expected_ema
    assert pytest.approx(strat.reading_as_list("SMA_10_T10")) == expected_sma_t10


@pytest.mark.usefixtures("candles", "expected_ema", "expected_sma_t10", "expected_obv_t10")
def test_hextial_multi_timeframes_shared_candles(
    candles, expected_ema, expected_sma_t10, expected_obv_t10
):
    strat = Hexital(
        "Test Stratergy",
        candles,
        [EMA(), SMA(timeframe="t10"), {"indicator": "OBV", "timeframe": "T10"}],
    )
    strat.calculate()

    candles_name = None
    for key in strat._candles.keys():
        if key != DEFAULT_CANDLES:
            candles_name = key

    assert len(strat._candles.keys()) == 2
    assert pytest.approx(strat.reading_as_list("EMA_10")) == expected_ema
    assert (
        strat._candles[candles_name].candles[-1].indicators.get("SMA_10_T10")
        == expected_sma_t10[-1]
        and strat._candles[candles_name].candles[-1].indicators.get("OBV_T10")
        == expected_obv_t10[-1]
    )


@pytest.mark.usefixtures("candles")
def test_hextial_multi_timeframes_get_candles(candles):
    strat = Hexital(
        "Test Stratergy",
        candles,
        [SMA(timeframe="t10"), OBV(timeframe="T10")],
    )
    strat.calculate()

    candles_name = None
    for key in strat._candles.keys():
        if key != DEFAULT_CANDLES:
            candles_name = key

    assert strat.candles(candles_name)[-1].indicators.get("SMA_10_T10") and strat.candles(
        candles_name
    )[-1].indicators.get("OBV_T10")


@pytest.mark.usefixtures("candles", "expected_sma_t10")
def test_hextial_multi_timeframe_reading(candles, expected_sma_t10):
    strat = Hexital("Test Stratergy", candles, [EMA(), SMA(timeframe="t10")])
    strat.calculate()
    assert pytest.approx(strat.reading("SMA_10_T10")) == expected_sma_t10[-1]


@pytest.mark.usefixtures("candles", "expected_ema", "expected_sma_t5")
def test_hextial_multi_timeframes_lifespan(candles, expected_ema, expected_sma_t5):
    strat = Hexital(
        "Test Stratergy",
        [],
        [EMA(), SMA(timeframe="t5")],
        candles_lifespan=timedelta(hours=1),
    )
    for candle in candles:
        strat.append(candle)

    assert pytest.approx(strat.reading_as_list("EMA_10")) == expected_ema[-61:]
    assert pytest.approx(strat.reading_as_list("SMA_10_T5"), 1.5e-02) == expected_sma_t5[-13:]
