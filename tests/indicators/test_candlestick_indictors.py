import pytest
from hexital import Hexital, indicators

from .indicator_testbase import IndicatorTestBase


class TestIndicators(IndicatorTestBase):
    @pytest.mark.usefixtures("candles", "expected_heikinashi_ema")
    def test_hextial_candlestick_heiknashi_ema(self, candles, expected_heikinashi_ema):
        strat = Hexital("Test Stratergy", candles, [indicators.EMA()], candlestick="HA")
        strat.calculate()
        assert self.verify(strat.indicators["EMA_10"].readings(), expected_heikinashi_ema)
