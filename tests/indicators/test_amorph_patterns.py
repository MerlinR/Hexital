import pytest
from hexital import indicators, patterns

from .indicator_testbase import IndicatorTestBase


class TestAmorphPatterns(IndicatorTestBase):
    @pytest.mark.usefixtures("candles", "expected_doji")
    def test_doji(self, candles, expected_doji):
        test = indicators.Amorph(analysis=patterns.doji, candles=candles)
        test.calculate()
        assert self.verify(test.readings, expected_doji)

    @pytest.mark.usefixtures("candles", "expected_dojistar")
    def test_dojistar(self, candles, expected_dojistar):
        test = indicators.Amorph(analysis=patterns.dojistar, candles=candles)
        test.calculate()
        assert self.verify(test.readings, expected_dojistar, acceptable_diff=1)

    @pytest.mark.usefixtures("candles", "expected_hammer")
    def test_hammer(self, candles, expected_hammer):
        test = indicators.Amorph(analysis=patterns.hammer, candles=candles)
        test.calculate()
        assert self.verify(test.readings, expected_hammer)

    @pytest.mark.usefixtures("candles", "expected_inverted_hammer")
    def test_inverted_hammer(self, candles, expected_inverted_hammer):
        test = indicators.Amorph(analysis=patterns.inverted_hammer, candles=candles)
        test.calculate()
        assert self.verify(test.readings, expected_inverted_hammer)
