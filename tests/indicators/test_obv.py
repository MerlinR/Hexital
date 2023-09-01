import deepdiff
import pytest
from hexital import OBV


@pytest.mark.usefixtures("candles", "expected_OBV")
def test_indicator(candles, expected_OBV):
    test = OBV(candles=candles)
    test.calculate()
    print(test.as_list)
    assert not deepdiff.DeepDiff(
        test.as_list,
        expected_OBV,
        significant_digits=1,
        number_format_notation="e",
        ignore_numeric_type_changes=True,
    )
