from hexital import Hexital, indicators

from .indicator_testbase import IndicatorTestBase


class TestIndicators(IndicatorTestBase):
    def test_hextial_candlestick_heiknashi_ema(self, candles, expected_heikinashi_ema):
        strategy = Hexital(
            "Test Stratergy", candles, [indicators.EMA()], candlestick="HA"
        )
        strategy.calculate()
        assert self.verify(
            strategy.indicators["EMA_10"].readings(), expected_heikinashi_ema
        )
