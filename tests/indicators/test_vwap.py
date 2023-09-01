import deepdiff
import pytest
from hexital import VWAP


@pytest.mark.usefixtures("candles", "expected_VWAP")
def test_indicator(candles, expected_VWAP):
    test = VWAP(candles=candles)
    test.calculate()
    print(test.as_list)
    assert not deepdiff.DeepDiff(
        test.as_list,
        expected_VWAP,
        significant_digits=1,
        number_format_notation="e",
        ignore_numeric_type_changes=True,
    )
