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

    mkt_id: str = None  # Exchange given ticker ID
    bid: float = None
    offer: float = None
    spread: float = None
    timestamp: datetime = field(default_factory=datetime.now)


@pytest.fixture(name="candles_30")
@pytest.mark.usefixtures("candles")
def fixture_candles_30(candles):
    return candles[0:30]


@pytest.fixture(name="candles_31st")
@pytest.mark.usefixtures("candles")
def fixture_candles_31st(candles):
    return candles[30]


def test_data(candles_30):
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
        9827.5,
        9889.3571,
        9235.704,
        9993.8274,
        9233.7486,
        9499.0106,
        10284.5334,
        10476.3874,
        11224.8267,
        11506.8432,
        11406.3819,
    ]

    test = EMA(candles=candles_30, period=20, input_value="close")
    test.calculate()

    assert test.as_list == expected


def test_data_append(candles_30, candles_31st):
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
        9827.5,
        9889.3571,
        9235.704,
        9993.8274,
        9233.7486,
        9499.0106,
        10284.5334,
        10476.3874,
        11224.8267,
        11506.8432,
        11406.3819,
        10804.1551,
    ]

    test = EMA(candles=candles_30, period=20, input_value="close")
    test.calculate()
    candles_30.append(candles_31st)
    test.calculate()

    assert test.as_list == expected
