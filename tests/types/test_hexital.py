import pytest
from hexital.core import Hexital
from hexital.exceptions import InvalidIndicator
from hexital.indicators import EMA, SMA


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


@pytest.mark.usefixtures("candles", "expected_sma")
def test_hextial_append(candles, expected_sma):
    new_candle = candles.pop()
    strat = Hexital("Test Stratergy", candles, [{"indicator": "SMA", "period": 10}])

    strat.calculate()
    assert pytest.approx(strat.reading_as_list("SMA")) != expected_sma

    strat.append(new_candle)

    assert pytest.approx(strat.reading_as_list("SMA")) == expected_sma


@pytest.mark.usefixtures("candles")
def test_hextial_append_invalid(candles):
    strat = Hexital("Test Stratergy", candles, [{"indicator": "SMA", "period": 10}])
    with pytest.raises(TypeError):
        strat.append([1, 2, 3])


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
