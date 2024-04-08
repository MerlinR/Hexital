import pytest
from hexital import indicators, patterns

from .indicator_testbase import IndicatorTestBase


class TestAmorphPatterns(IndicatorTestBase):
    @pytest.mark.usefixtures("candles", "expected_doji")
    def test_doji(self, candles, expected_doji):
        test = indicators.Amorph(analysis=patterns.doji, candles=candles)
        test.calculate()
        assert self.verify(test.as_list(), expected_doji)

    @pytest.mark.usefixtures("candles", "expected_hammer")
    def test_hammer(self, candles, expected_hammer):
        test = indicators.Amorph(analysis=patterns.hammer, candles=candles)
        test.calculate()
        assert self.verify(test.as_list(), expected_hammer)
