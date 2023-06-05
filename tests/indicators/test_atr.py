import deepdiff
import pytest
from hexital import ATR


@pytest.mark.usefixtures("candles", "expected_ATR")
def test_indicator(candles, expected_ATR):
    test = ATR(candles=candles)
    test.calculate()
    print(test.get_as_list())
    assert not deepdiff.DeepDiff(
        test.get_as_list()[-340:],
        expected_ATR[-340:],
        ignore_order=True,
        significant_digits=1,
    )
