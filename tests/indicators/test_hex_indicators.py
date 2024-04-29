import pytest
from hexital import Hexital, indicators

from .indicator_testbase import IndicatorTestBase


class TestHexPatterns(IndicatorTestBase):
    @pytest.mark.usefixtures("candles", "expected_counter_bull")
    def test_counter(self, candles, expected_counter_bull):
        strat = Hexital(
            "Test counter",
            candles,
            [indicators.Supertrend(), indicators.Counter(input_value="Supertrend_7.direction")],
        )
        strat.calculate()
        assert self.verify(strat.indicators["COUNT_Supertrend_7"].as_list(), expected_counter_bull)

    @pytest.mark.usefixtures("candles", "expected_counter_bear")
    def test_counter_inverse(self, candles, expected_counter_bear):
        strat = Hexital(
            "Test counter",
            candles,
            [
                indicators.Supertrend(),
                indicators.Counter(input_value="Supertrend_7.direction", count_value=-1),
            ],
        )
        strat.calculate()

        assert self.verify(strat.indicators["COUNT_Supertrend_7"].as_list(), expected_counter_bear)

    @pytest.mark.usefixtures("candles", "expected_highestlowest")
    def test_highest_lowest(self, candles, expected_highestlowest):
        test = indicators.HighestLowest(candles=candles)
        test.calculate()
        print(test.as_list())
        assert self.verify(test.as_list(), expected_highestlowest)

    @pytest.mark.usefixtures("candles", "expected_stdevthres")
    def test_stdevthres(self, candles, expected_stdevthres):
        test = indicators.StandardDeviationThreshold(candles=candles)
        test.calculate()
        assert self.verify(test.as_list(), expected_stdevthres)
