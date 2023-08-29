import deepdiff
import pytest
from hexital import ATR


@pytest.mark.usefixtures("candles", "expected_ATR")
def test_indicator(candles, expected_ATR):
    test = ATR(candles=candles)
    test.calculate()
    assert not deepdiff.DeepDiff(
        test.as_list,
        expected_ATR,
        ignore_order=True,
        significant_digits=1,
    )
