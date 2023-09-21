from dataclasses import dataclass
from typing import List

import pytest
from hexital.core import Candle, Indicator
from hexital.exceptions import InvalidTimeFrame


@dataclass(kw_only=True)
class FakeIndicator(Indicator):
    indicator_name: str = "Fake"
    period: int = 10
    input_value: str = "close"

    def _generate_name(self) -> str:
        return f"{self.indicator_name}_{self.period}"

    def _calculate_reading(self, index: int) -> float | dict | None:
        return 100.0


def remove_indicators(candles: List[Candle]) -> List[Candle]:
    for candle in candles:
        candle.sub_indicators = {}
        candle.indicators = {}
    return candles


@pytest.mark.usefixtures("minimal_candles", "minimal_candles_t5")
def test_round_down_timestamp(
    minimal_candles: List[Candle], minimal_candles_t5: List[Candle]
):
    test = FakeIndicator(candles=minimal_candles, timeframe="t5")
    assert test.candles[0].timestamp == minimal_candles_t5[0].timestamp


@pytest.mark.usefixtures("minimal_candles", "minimal_candles_t5")
def test_collapse_candles_first(
    minimal_candles: List[Candle], minimal_candles_t5: List[Candle]
):
    minimal_candles = remove_indicators(minimal_candles)
    test = FakeIndicator(candles=minimal_candles, timeframe="t5")
    assert test.candles[0] == minimal_candles_t5[0]


@pytest.mark.usefixtures("minimal_candles", "minimal_candles_t5")
def test_collapse_candles_last(
    minimal_candles: List[Candle], minimal_candles_t5: List[Candle]
):
    minimal_candles = remove_indicators(minimal_candles)
    test = FakeIndicator(candles=minimal_candles, timeframe="t5")

    assert test.candles[-1] == minimal_candles_t5[-1]


@pytest.mark.usefixtures("minimal_candles", "minimal_candles_t5")
def test_collapse_candles_minutes_t5(
    minimal_candles: List[Candle], minimal_candles_t5: List[Candle]
):
    minimal_candles = remove_indicators(minimal_candles)
    test = FakeIndicator(candles=minimal_candles, timeframe="t5")

    assert test.candles == minimal_candles_t5


@pytest.mark.usefixtures("minimal_candles", "minimal_candles_t10")
def test_collapse_candles_minutes_t10(
    minimal_candles: List[Candle], minimal_candles_t10: List[Candle]
):
    minimal_candles = remove_indicators(minimal_candles)
    test = FakeIndicator(candles=minimal_candles, timeframe="t10")

    assert test.candles == minimal_candles_t10


@pytest.mark.usefixtures("minimal_candles", "minimal_candles_t5")
def test_collapse_candles_minutes_append_seconds(
    minimal_candles: List[Candle], minimal_candles_t5: List[Candle]
):
    minimal_candles = remove_indicators(minimal_candles)
    test = FakeIndicator(candles=minimal_candles[:11], timeframe="t5")
    assert test.candles == minimal_candles_t5[:2]
    test.append(minimal_candles[11:])
    test.candles = remove_indicators(test.candles)
    assert test.candles == minimal_candles_t5


@pytest.mark.usefixtures("minimal_candles")
def test_invalid_timeframe(minimal_candles: List[Candle]):
    with pytest.raises(InvalidTimeFrame):
        test = FakeIndicator(candles=minimal_candles, timeframe="q10")
