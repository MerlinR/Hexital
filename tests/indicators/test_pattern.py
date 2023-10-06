from typing import Optional

import deepdiff
import pytest
from hexital import indicators, patterns
from hexital.exceptions import InvalidPattern


class TestPatterns:
    def verfiy(
        self,
        result: list,
        expected: list,
        amount: Optional[int] = None,
        verbose: bool = False,
    ) -> bool:

        if amount is not None:
            result = result[-abs(amount) :]
            expected = expected[-abs(amount) :]

        self.show_results(result, expected, verbose)

        diff_result = not deepdiff.DeepDiff(
            result,
            expected,
            significant_digits=1,
            number_format_notation="e",
            ignore_numeric_type_changes=True,
        )

        correlation = False
        if not diff_result:
            correlation = self.correlation_validation(result, expected)

        return any([diff_result, correlation])

    def correlation_validation(
        self, result: list, expected: list, accuracy: float = 0.95
    ):
        correlation = 0

        if isinstance(result[0], dict):
            correlations = 0.0
            for key in expected[0].keys():
                correlations += self.correlation_coefficient(
                    [row[key] for row in result], [row[key] for row in expected]
                )

            correlation = correlations / len(expected[0].keys())
        else:
            correlation = self.correlation_coefficient(result, expected)

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
        for index, _ in enumerate(result):
            if result[index] is not None and expected[index] is not None:
                r_numerator += (result[index] - res_mean) * (expected[index] - exp_mean)

        # r denominator
        r_denominator = res_stand_deviation * exp_stand_deviation

        correlation = r_numerator / r_denominator
        return round(correlation, 4)

    def calc_mean(self, data: list):
        total = 0
        length = 0
        for value in data:
            if value is not None:
                length += 1
                total += float(value)
        return total / length

    def standard_deviation(self, data: list):
        data_mean = self.calc_mean(data)
        dev = 0.0
        for val in data:
            if data_mean is not None and val is not None:
                dev += (val - data_mean) ** 2
        dev = dev ** (1 / 2.0)
        return dev

    def show_results(self, result: list, expected: list, verbose: bool):
        for i, (res, exp) in enumerate(zip(result, expected)):
            if deepdiff.DeepDiff(
                res,
                exp,
                significant_digits=1,
                number_format_notation="e",
                ignore_numeric_type_changes=True,
            ):
                print("\033[91m" + f"{i}: {res} != {exp}" + "\033[0m")
            elif verbose:
                print("\033[92m" + f"{i}: {res} == {exp}" + "\033[0m")

    @pytest.mark.usefixtures("candles")
    def test_invalid_pattern(self, candles):
        with pytest.raises(InvalidPattern):
            indicators.Pattern(pattern="FUCK", candles=candles)

    @pytest.mark.usefixtures("candles")
    def test_string_pattern(self, candles):
        test = indicators.Pattern(pattern="doji", candles=candles)
        test.calculate()
        assert test.reading() is not None

    @pytest.mark.usefixtures("candles")
    def test_method_pattern(self, candles):
        test = indicators.Pattern(pattern=patterns.doji, candles=candles)
        test.calculate()
        assert test.reading() is not None

    @pytest.mark.usefixtures("candles")
    def test_pattern_multi_arguments(self, candles):
        test = indicators.Pattern(pattern=patterns.doji, candles=candles, length=20)
        test.calculate()
        assert test.name == "doji_20"

    @pytest.mark.usefixtures("candles")
    def test_pattern_dict_arguments(self, candles):
        test = indicators.Pattern(
            pattern=patterns.doji, candles=candles, args={"length": 20}
        )
        test.calculate()
        assert test.name == "doji_20"

    @pytest.mark.usefixtures("candles")
    def test_pattern_merged_aguments(self, candles):
        test = indicators.Pattern(
            pattern=patterns.doji,
            candles=candles,
            length=20,
            fullname_override="MERGED_ARGS",
        )
        test.calculate()
        assert test.name == "MERGED_ARGS"

    @pytest.mark.usefixtures("candles", "expected_doji")
    def test_doji(self, candles, expected_doji):
        test = indicators.Pattern(pattern=patterns.doji, candles=candles)
        test.calculate()
        assert self.verfiy(test.as_list, expected_doji)
