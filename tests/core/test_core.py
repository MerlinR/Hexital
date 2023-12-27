from dataclasses import dataclass, field
from datetime import datetime

import pytest
from hexital import EMA, Candle


@dataclass
class InheritedCandle(Candle):
    """
    Candle is a tick of market data, holds more then Candle,
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


def test_data(candles_30, expected_ema):
    test = EMA(candles=candles_30, input_value="close")
    test.calculate()
    assert pytest.approx(test.as_list) == expected_ema[0:30]


def test_data_append(candles_30, candles_31st, expected_ema):
    test = EMA(candles=candles_30, input_value="close")
    test.calculate()
    candles_30.append(candles_31st)
    test.calculate()

    assert pytest.approx(test.as_list) == expected_ema[0:31]
