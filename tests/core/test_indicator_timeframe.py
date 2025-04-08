from dataclasses import dataclass, field
from typing import List, Optional

import pytest
from hexital import TimeFrame
from hexital.core.candle import Candle
from hexital.core.indicator import Indicator
from test_candlestick import FakeType


@dataclass(kw_only=True)
class FakeIndicator(Indicator):
    candles: list = field(default_factory=list)
    timeframe: Optional[str | TimeFrame] = None
    indicator_name: str = "Fake"
    period: int = 10
    source: str = "close"

    def _generate_name(self) -> str:
        return f"{self.indicator_name}_{self.period}"

    def _calculate_reading(self, index: int) -> float | dict | None:
        return self.reading("open") + self.reading("close")


def remove_indicators(candles: List[Candle]) -> List[Candle]:
    for candle in candles:
        candle.sub_indicators = {}
        candle.indicators = {}
    return candles


@pytest.mark.usefixtures("minimal_candles", "minimal_candles_t5")
def test_resample_candles_minutes_t5(
    minimal_candles: List[Candle], minimal_candles_t5: List[Candle]
):
    minimal_candles = remove_indicators(minimal_candles)
    test = FakeIndicator(candles=minimal_candles, timeframe="t5")

    assert test.candles == minimal_candles_t5


@pytest.mark.usefixtures("minimal_candles", "minimal_candles_t10")
def test_resample_candles_minutes_t10(
    minimal_candles: List[Candle], minimal_candles_t10: List[Candle]
):
    minimal_candles = remove_indicators(minimal_candles)
    test = FakeIndicator(candles=minimal_candles, timeframe="t10")

    assert test.candles == minimal_candles_t10


@pytest.mark.usefixtures("minimal_candles", "minimal_candles_t10")
def test_resample_candles_minutes_t10_enum(
    minimal_candles: List[Candle], minimal_candles_t10: List[Candle]
):
    minimal_candles = remove_indicators(minimal_candles)
    test = FakeIndicator(candles=minimal_candles, timeframe=TimeFrame.MINUTE10)

    assert test.candles == minimal_candles_t10


@pytest.mark.usefixtures("minimal_candles", "minimal_candles_t10")
def test_resample_candles_minutes_t10_enum_name(
    minimal_candles: List[Candle], minimal_candles_t10: List[Candle]
):
    minimal_candles = remove_indicators(minimal_candles)
    test = FakeIndicator(candles=minimal_candles, timeframe=TimeFrame.MINUTE10)

    assert test.name == "Fake_10_T10"


@pytest.mark.usefixtures("minimal_candles", "minimal_candles_t5")
def test_resample_candles_minutes_t5_partial(
    minimal_candles: List[Candle], minimal_candles_t5: List[Candle]
):
    minimal_candles_t5[0].indicators = {"Fake_10_T5": 25631}
    minimal_candles_t5[1].indicators = {"Fake_10_T5": 20069}
    minimal_candles_t5[2].indicators = {"Fake_10_T5": 33201}
    minimal_candles_t5[3].indicators = {"Fake_10_T5": 33184}

    minimal_candles = remove_indicators(minimal_candles)
    test = FakeIndicator(candles=minimal_candles[:3], timeframe="t5")
    test.calculate()
    test.append(minimal_candles[3:])

    assert test.candles == minimal_candles_t5


class TestIndicatorCandlestickType:
    @pytest.mark.usefixtures("minimal_candles")
    def test_indicator_candlestick_type(self, minimal_candles):
        test_indicator = FakeIndicator(candles=minimal_candles, candlestick=FakeType())

        assert (
            isinstance(test_indicator.candlestick, FakeType)
            and test_indicator.candles[-1].tag == "Fake_Type"
        )

    @pytest.mark.usefixtures("minimal_candles")
    def test_indicator_candlestick_type_inuse(self, minimal_candles):
        test_indicator = FakeIndicator(
            candles=minimal_candles, candlestick=FakeType(), timeframe="T5"
        )

        assert (
            isinstance(test_indicator.candlestick, FakeType)
            and test_indicator.candles[-1].tag == "Fake_Type"
        )
