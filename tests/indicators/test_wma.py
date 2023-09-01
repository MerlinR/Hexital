import deepdiff
import pytest
from hexital import WMA


@pytest.mark.usefixtures("candles", "expected_WMA")
def test_indicator(candles, expected_WMA):
    test = WMA(candles=candles)
    test.calculate()
    print(test.as_list)
    assert not deepdiff.DeepDiff(
        test.as_list,
        expected_WMA,
        significant_digits=1,
        number_format_notation="e",
        ignore_numeric_type_changes=True,
    )
