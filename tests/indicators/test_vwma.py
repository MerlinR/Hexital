import deepdiff
import pytest
from hexital import VWMA


@pytest.mark.usefixtures("candles", "expected_VWMA")
def test_indicator(candles, expected_VWMA):
    test = VWMA(candles=candles)
    test.calculate()
    print(test.as_list)
    assert not deepdiff.DeepDiff(
        test.as_list,
        expected_VWMA,
        significant_digits=1,
        number_format_notation="e",
        ignore_numeric_type_changes=True,
    )
