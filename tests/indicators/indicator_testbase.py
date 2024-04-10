import math
from typing import Optional

import deepdiff


class IndicatorTestBase:
    def verify(
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

    def correlation_validation(self, result: list, expected: list, accuracy: float = 0.95):
        correlation = 0

        if isinstance(result[0], dict):
            correlations = 0.0
            for key in expected[0].keys():
                correlations += self.correlation_coefficient(
                    [row[key] for row in result], [row[key] for row in expected]
                )

            correlation = round(correlations / len(expected[0].keys()), 4)
        else:
            correlation = self.correlation_coefficient(result, expected)

        print(f"Correlation: {correlation}")
        return correlation >= accuracy

    def correlation_coefficient(self, result: list, expected: list):
        # https://stackoverflow.com/questions/3949226/calculating-pearson-correlation-and-significance-in-python
        if len(result) != len(expected):
            return 0

        result_mean = self.calc_mean(result)
        expected_means = self.calc_mean(expected)

        numerator = 0
        x = 0
        y = 0

        for i in range(len(expected)):
            r_diff = result[i] if result[i] is not None else 0 - result_mean
            e_diff = expected[i] if expected[i] is not None else 0 - expected_means
            numerator += r_diff * e_diff
            x += r_diff * r_diff
            y += e_diff * e_diff

        denominator = math.sqrt(x * y)

        if denominator == 0:
            return 0

        return numerator / denominator

    def calc_mean(self, data: list):
        total = 0
        for value in data:
            if value is not None:
                total += float(value)
        return total / len(data)

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
