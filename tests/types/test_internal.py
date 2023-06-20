from dataclasses import dataclass, field
from datetime import datetime

import pytest
from hexital import EMA, OHLCV


@dataclass
class Candle(OHLCV):
    """
    Candle is a tick of market data, holds more then OHLCV,
    can merge so mutiple second data becomes minute;
    aswell asconvert to a dataframe
    """

    mkt_id: str = None  # Exchange given ticker ID, E.G IX.I.NASDAQ.IP
    bid: float = None
    offer: float = None
    spread: float = None
    timestamp: datetime = field(default_factory=datetime.now)


@pytest.fixture(name="nasdaq_candles_30")
@pytest.mark.usefixtures("candles")
def fixture_nasdaq_data_30(candles):
    return candles[0:30]


@pytest.fixture(name="nasdaq_candles_31st")
@pytest.mark.usefixtures("candles")
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


@pytest.mark.usefixtures("nasdaq_candles", "expected_EMA")
def test_hextial_multi_dict(nasdaq_candles, expected_EMA):
    test = EMA(candles=OHLCV.from_dicts(nasdaq_candles))
    test.calculate()
    print(test.get_as_list())
    assert pytest.approx(test.get_as_list()) == expected_EMA
