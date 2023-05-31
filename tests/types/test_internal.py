import pytest
from hexital import EMA, Candle


@pytest.fixture(name="candles")
@pytest.mark.usefixtures("nasdaq_candles")
def fixture_nasdaq_data(nasdaq_candles):
    return Candle.from_dicts(nasdaq_candles)


@pytest.fixture(name="nasdaq_candles_30")
def fixture_nasdaq_data_30(candles):
    return candles[0:30]


@pytest.fixture(name="nasdaq_candles_31st")
def fixture_nasdaq_data_31st(candles):
    return candles[30]


def test_data(nasdaq_candles_30):
    expected = [
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        11817.1465,
        11842.3125,
        11856.8027,
        11900.6215,
        11911.2985,
        11925.591,
        11949.3662,
        11962.4046,
        11942.5785,
        11885.1919,
        11782.7194,
    ]

    test = EMA(candles=nasdaq_candles_30, period=20, input_value="close")
    test.calculate()

    assert test.get_as_list() == expected


def test_data_append(nasdaq_candles_30, nasdaq_candles_31st):
    expected = [
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        11817.1465,
        11842.3125,
        11856.8027,
        11900.6215,
        11911.2985,
        11925.591,
        11949.3662,
        11962.4046,
        11942.5785,
        11885.1919,
        11782.7194,
        11691.827,
    ]

    test = EMA(candles=nasdaq_candles_30, period=20, input_value="close")
    test.calculate()
    nasdaq_candles_30.append(nasdaq_candles_31st)
    test.calculate()

    assert test.get_as_list() == expected
