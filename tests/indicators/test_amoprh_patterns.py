from hexital import indicators, patterns

from .indicator_testbase import IndicatorTestBase


class TestAmorphPatterns(IndicatorTestBase):
    def test_doji(self, candles, expected_doji):
        test = indicators.Amorph(analysis=patterns.doji, candles=candles)
        test.calculate()
        assert self.verify(test.series(), expected_doji)

    def test_dojistar(self, candles, expected_dojistar):
        test = indicators.Amorph(analysis=patterns.dojistar, candles=candles)
        test.calculate()
        assert self.verify(test.series(), expected_dojistar, acceptable_diff=1)

    def test_hammer(self, candles, expected_hammer):
        test = indicators.Amorph(analysis=patterns.hammer, candles=candles)
        test.calculate()
        assert self.verify(test.series(), expected_hammer)

    def test_inverted_hammer(self, candles, expected_inverted_hammer):
        test = indicators.Amorph(analysis=patterns.inverted_hammer, candles=candles)
        test.calculate()
        assert self.verify(test.series(), expected_inverted_hammer)
