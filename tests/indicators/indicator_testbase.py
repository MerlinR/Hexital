import math
from typing import Dict, List

# math.isclose to 0.5%
ACCURACY_PER = 0.005


class IndicatorTestBase:
    def verify(
        self,
        result: list,
        expected: list,
        amount: int = 0,
        acceptable_diff: int = 0,
        verbose: bool = False,
    ) -> bool:
        if amount is not None:
            result = result[-abs(amount) :]
            expected = expected[-abs(amount) :]

        diff_results = self.deepdiff(result, expected)

        self.show_results(diff_results, acceptable_diff, verbose)

        return diff_results.get("differences") <= acceptable_diff

    def show_results(self, results: Dict[str, int | list], acceptable_diff: int, verbose: bool):
        print(f"Differences: {results['differences']}")

        for row in results["results"]:
            if row[-1] is False:
                print("\033[91m" + f"{row[0]}: {row[1]}\t!=\t{row[2]}" + "\033[0m")
            elif verbose:
                print("\033[92m" + f"{row[0]}: {row[1]}\t==\t{row[2]}" + "\033[0m")

    def deepdiff(
        self,
        result: List[dict | float | bool] | dict | float | bool,
        expected: List[dict | float | bool] | dict | float | bool,
    ) -> Dict[str, int | list]:
        differences = 0
        results = []

        if not isinstance(result, list):
            result = [result]
        if not isinstance(expected, list):
            expected = [expected]

        for i, (res, exp) in enumerate(zip(result, expected)):
            results.append([i, res, exp, True])

            if res is None or exp is None:
                if (res is None and exp == 0) or res == 0 and exp is None:
                    continue
                elif res != exp:
                    differences += 1
                    results[-1][-1] = False
            elif isinstance(res, bool):
                if res != exp:
                    differences += 1
                    results[-1][-1] = False
            elif isinstance(res, (float, int)) and isinstance(exp, (float, int)):
                if not math.isclose(res, exp, rel_tol=ACCURACY_PER):
                    differences += 1
                    results[-1][-1] = False
            elif isinstance(res, dict) and isinstance(exp, dict):
                if not self.compare_dict(res, exp):
                    differences += 1
                    results[-1][-1] = False

        return {"differences": differences, "results": results}

    @staticmethod
    def compare_dict(
        value_a: Dict[str, int | float | bool | None],
        value_b: Dict[str, int | float | bool | None],
    ) -> bool:
        fields = [field for field in value_a.keys() if field in value_b.keys()]
        fields = [field for field in value_b.keys() if field in fields]

        for field in fields:
            res = value_a[field]
            exp = value_b[field]
            if res is None or exp is None:
                if (res is None and exp == 0) or res == 0 and exp is None:
                    continue
                elif res != exp:
                    return False
            elif isinstance(res, bool):
                if res != exp:
                    return False
            elif isinstance(res, (float, int)) and isinstance(exp, (float, int)):
                if not math.isclose(res, exp, rel_tol=ACCURACY_PER):
                    return False

        return True
