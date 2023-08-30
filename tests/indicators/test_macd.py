import deepdiff
import pytest
from hexital import MACD


@pytest.mark.usefixtures("candles", "expected_MACD")
def test_indicator(candles, expected_MACD):
    test = MACD(candles=candles)
    test.calculate()

    assert not deepdiff.DeepDiff(
        test.as_list[-400:],
        expected_MACD[-400:],
        significant_digits=1,
        number_format_notation="e",
        ignore_numeric_type_changes=True,
    )
