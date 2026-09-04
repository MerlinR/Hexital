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

    def test_bullish_engulfing(self, candles, expected_bullish_engulfing):
        test = indicators.Amorph(analysis=patterns.bullish_engulfing, candles=candles)
        test.calculate()
        assert self.verify(test.series(), expected_bullish_engulfing)

    def test_bearish_engulfing(self, candles, expected_bearish_engulfing):
        test = indicators.Amorph(analysis=patterns.bearish_engulfing, candles=candles)
        test.calculate()
        assert self.verify(test.series(), expected_bearish_engulfing)

    def test_bullish_harami(self, candles, expected_bullish_harami):
        test = indicators.Amorph(analysis=patterns.bullish_harami, candles=candles)
        test.calculate()
        assert self.verify(test.series(), expected_bullish_harami)

    def test_bearish_harami(self, candles, expected_bearish_harami):
        test = indicators.Amorph(analysis=patterns.bearish_harami, candles=candles)
        test.calculate()
        assert self.verify(test.series(), expected_bearish_harami)

    def test_hanging_man(self, candles, expected_hanging_man):
        test = indicators.Amorph(analysis=patterns.hanging_man, candles=candles)
        test.calculate()
        assert self.verify(test.series(), expected_hanging_man)

    def test_shooting_star(self, candles, expected_shooting_star):
        test = indicators.Amorph(analysis=patterns.shooting_star, candles=candles)
        test.calculate()
        assert self.verify(test.series(), expected_shooting_star)

    def test_spinning_top(self, candles, expected_spinning_top):
        test = indicators.Amorph(analysis=patterns.spinning_top, candles=candles)
        test.calculate()
        assert self.verify(test.series(), expected_spinning_top)
