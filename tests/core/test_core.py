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


@pytest.fixture
def fixture_candles_30(candles):
    return candles[0:30]


@pytest.fixture
def fixture_candles_31st(candles):
    return candles[30]


def test_data(fixture_candles_30, expected_ema):
    test = EMA(candles=fixture_candles_30, source="close")
    test.calculate()
    assert pytest.approx(test.readings) == expected_ema[0:30]


def test_data_append(fixture_candles_30, fixture_candles_31st, expected_ema):
    test = EMA(candles=fixture_candles_30, source="close")
    test.calculate()
    fixture_candles_30.append(fixture_candles_31st)
    test.calculate()

    assert pytest.approx(test.readings) == expected_ema[0:31]
