import pytest
from hexital.indicators import EMA, SMA
from hexital.types import Hexital


@pytest.mark.usefixtures("candles", "expected_EMA")
def test_hextial_single(candles, expected_EMA):
    strat = Hexital("Test Stratergy", candles)
    strat.add_indicator(EMA())
    strat.calculate()
    assert pytest.approx(strat.reading_as_list("EMA_10")) == expected_EMA


@pytest.mark.usefixtures("candles", "expected_EMA", "expected_SMA")
def test_hextial_multi(candles, expected_EMA, expected_SMA):
    strat = Hexital("Test Stratergy", candles, [EMA(), SMA()])
    strat.calculate()
    assert (
        pytest.approx(strat.reading_as_list("EMA_10")) == expected_EMA
        and pytest.approx(strat.reading_as_list("SMA_10")) == expected_SMA
    )


@pytest.mark.usefixtures("candles", "expected_EMA", "expected_SMA")
def test_hextial_multi_dict(candles, expected_EMA, expected_SMA):
    strat = Hexital("Test Stratergy", candles, [EMA(), {"indicator": "SMA"}])
    strat.calculate()
    assert (
        pytest.approx(strat.reading_as_list("EMA_10")) == expected_EMA
        and pytest.approx(strat.reading_as_list("SMA_10")) == expected_SMA
    )


@pytest.mark.usefixtures("candles", "expected_EMA")
def test_hextial_multi_dict_invalid(candles, expected_EMA):
    strat = Hexital("Test Stratergy", candles, [EMA(), {"indicator": "FUCK"}])
    strat.calculate()
    assert pytest.approx(strat.reading_as_list("EMA_10")) == expected_EMA


@pytest.mark.usefixtures("candles", "expected_EMA")
def test_hextial_multi_dict_invalid_missing(candles, expected_EMA):
    strat = Hexital("Test Stratergy", candles, [EMA(), {"period": 10}])
    strat.calculate()
    assert pytest.approx(strat.reading_as_list("EMA_10")) == expected_EMA


@pytest.mark.usefixtures("candles", "expected_EMA", "expected_SMA")
def test_hextial_multi_dict_append(candles, expected_EMA, expected_SMA):
    strat = Hexital("Test Stratergy", candles, [EMA()])
    strat.add_indicator({"indicator": "SMA"})
    strat.calculate()
    assert (
        pytest.approx(strat.reading_as_list("EMA_10")) == expected_EMA
        and pytest.approx(strat.reading_as_list("SMA_10")) == expected_SMA
    )


@pytest.mark.usefixtures("candles")
def test_hextial_dict_arguments(candles):
    strat = Hexital("Test Stratergy", candles, [{"indicator": "SMA", "period": 20}])
    assert strat.get_indicator("SMA_20")


@pytest.mark.usefixtures("candles", "expected_SMA")
def test_hextial_read(candles, expected_SMA):
    strat = Hexital("Test Stratergy", candles, [{"indicator": "SMA", "period": 10}])
    strat.calculate()
    assert pytest.approx(strat.read("SMA")) == expected_SMA[-1]


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


@pytest.mark.usefixtures("candles", "expected_SMA")
def test_hextial_append(candles, expected_SMA):
    new_candle = candles.pop()
    strat = Hexital("Test Stratergy", candles, [{"indicator": "SMA", "period": 10}])

    strat.calculate()
    assert pytest.approx(strat.reading_as_list("SMA")) != expected_SMA

    strat.append(new_candle)

    assert pytest.approx(strat.reading_as_list("SMA")) == expected_SMA


@pytest.mark.usefixtures("candles", "expected_EMA", "expected_SMA")
def test_hextial_purge(candles, expected_EMA, expected_SMA):
    strat = Hexital("Test Stratergy", candles, [EMA(), {"indicator": "SMA"}])
    strat.calculate()

    assert strat.has_reading("SMA") and strat.has_reading("EMA")
    strat.purge_readings("SMA_10")

    assert not strat.has_reading("SMA") and strat.has_reading("EMA")


@pytest.mark.usefixtures("candles", "expected_EMA", "expected_SMA")
def test_hextial_remove_indicator(candles, expected_EMA, expected_SMA):
    strat = Hexital("Test Stratergy", candles, [EMA(), {"indicator": "SMA"}])
    strat.calculate()

    assert strat.has_reading("SMA")

    strat.remove_indicator("SMA_10")

    assert not any(
        indicator for indicator in strat.indicators if indicator.name == "SMA_10"
    )
