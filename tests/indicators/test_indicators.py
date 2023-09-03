from typing import Optional

import deepdiff
import pytest
from hexital import indicators


class TestIndicators:
    def verfiy(self, result: list, expected: list, amount: Optional[int] = None) -> bool:

        if amount is not None:
            result = result[-abs(amount) :]
            expected = expected[-abs(amount) :]

        self.show_results(result, expected)

        diff_result = not deepdiff.DeepDiff(
            result,
            expected,
            significant_digits=1,
            number_format_notation="e",
            ignore_numeric_type_changes=True,
        )

        correlation = self.correlation_validation(result, expected)

        return any([diff_result, correlation])

    def correlation_validation(
        self, result: list, expected: list, accuracy: float = 0.97
    ):
        correlation = 0

        if isinstance(result[0], float):
            correlation = self.correlation_coefficient(result, expected)
        elif isinstance(result[0], dict):
            correlations = 0.0
            for key in expected[0].keys():
                correlations += self.correlation_coefficient(
                    [row[key] for row in result], [row[key] for row in expected]
                )

            correlation = correlations / len(expected[0].keys())

        print(f"Correlation: {correlation}")
        return correlation >= accuracy

    def correlation_coefficient(self, result: list, expected: list):

        # First establish the means and standard deviations for both lists.
        res_mean = self.calc_mean(result)
        exp_mean = self.calc_mean(expected)
        res_stand_deviation = self.standard_deviation(result)
        exp_stand_deviation = self.standard_deviation(expected)

        # r numerator
        r_numerator = 0.0
        for index in range(len(result)):
            if result[index] is not None and expected[index] is not None:
                r_numerator += (result[index] - res_mean) * (expected[index] - exp_mean)

        # r denominator
        r_denominator = res_stand_deviation * exp_stand_deviation

        correlation = r_numerator / r_denominator
        return round(correlation, 4)

    def calc_mean(self, data: list):
        total = 0
        for value in data:
            if value is not None:
                total += float(value)
        return total / len(data)

    def standard_deviation(self, data: list):
        data_mean = self.calc_mean(data)
        dev = 0.0
        for val in data:
            if data_mean is not None and val is not None:
                dev += (val - data_mean) ** 2
        dev = dev ** (1 / 2.0)
        return dev

    def show_results(self, result: list, expected: list):
        for i, (res, exp) in enumerate(zip(result, expected)):
            print(f"{i}: {res} == {exp}")

    @pytest.mark.usefixtures("candles", "expected_atr")
    def test_atr(self, candles, expected_atr):
        test = indicators.ATR(candles=candles)
        test.calculate()
        assert self.verfiy(test.as_list, expected_atr)

    @pytest.mark.usefixtures("candles", "expected_atr_20")
    def test_atr_20(self, candles, expected_atr_20):
        test = indicators.ATR(candles=candles, period=20)
        test.calculate()
        assert self.verfiy(test.as_list, expected_atr_20)

    @pytest.mark.usefixtures("candles", "expected_ema")
    def test_ema(self, candles, expected_ema):
        test = indicators.EMA(candles=candles)
        test.calculate()
        assert self.verfiy(test.as_list, expected_ema)

    @pytest.mark.usefixtures("candles", "expected_kc")
    def test_kc(self, candles, expected_kc):
        test = indicators.KC(candles=candles)
        test.calculate()
        assert self.verfiy(test.as_list, expected_kc)

    @pytest.mark.usefixtures("candles", "expected_macd")
    def test_macd(self, candles, expected_macd):
        test = indicators.MACD(candles=candles)
        test.calculate()
        assert self.verfiy(test.as_list, expected_macd, amount=400)

    @pytest.mark.usefixtures("candles", "expected_obv")
    def test_obv(self, candles, expected_obv):
        test = indicators.OBV(candles=candles)
        test.calculate()
        print(test.as_list)
        assert self.verfiy(test.as_list, expected_obv)

    @pytest.mark.usefixtures("candles", "expected_rma")
    def test_rma(self, candles, expected_rma):
        test = indicators.RMA(candles=candles)
        test.calculate()
        assert self.verfiy(test.as_list, expected_rma, amount=470)

    @pytest.mark.usefixtures("candles", "expected_rsi")
    def test_rsi(self, candles, expected_rsi):
        test = indicators.RSI(candles=candles)
        test.calculate()
        assert self.verfiy(test.as_list, expected_rsi)

    @pytest.mark.usefixtures("candles", "expected_sma")
    def test_sma(self, candles, expected_sma):
        test = indicators.SMA(candles=candles)
        test.calculate()
        assert self.verfiy(test.as_list, expected_sma)

    @pytest.mark.usefixtures("candles", "expected_sma_3")
    def test_sma_3(self, candles, expected_sma_3):
        test = indicators.SMA(candles=candles, period=3)
        test.calculate()
        assert self.verfiy(test.as_list, expected_sma_3)

    @pytest.mark.usefixtures("candles", "expected_stoch")
    def test_stoch(self, candles, expected_stoch):
        test = indicators.STOCH(candles=candles)
        test.calculate()
        assert self.verfiy(test.as_list, expected_stoch)

    @pytest.mark.usefixtures("candles", "expected_tr")
    def test_tr(self, candles, expected_tr):
        test = indicators.TR(candles=candles)
        test.calculate()
        assert self.verfiy(test.as_list, expected_tr)

    @pytest.mark.usefixtures("candles", "expected_vwap")
    def test_vwap(self, candles, expected_vwap):
        test = indicators.VWAP(candles=candles)
        test.calculate()
        assert self.verfiy(test.as_list, expected_vwap)

    @pytest.mark.usefixtures("candles", "expected_vwma")
    def test_vwma(self, candles, expected_vwma):
        test = indicators.VWMA(candles=candles)
        test.calculate()
        assert self.verfiy(test.as_list, expected_vwma)

    @pytest.mark.usefixtures("candles", "expected_wma")
    def test_wma(self, candles, expected_wma):
        test = indicators.WMA(candles=candles)
        test.calculate()
        assert self.verfiy(test.as_list, expected_wma)
