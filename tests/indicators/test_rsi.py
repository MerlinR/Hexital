import deepdiff
import pytest
from hexital import RSI


@pytest.mark.usefixtures("candles", "expected_RSI")
def test_indicator(candles, expected_RSI):
    test = RSI(candles=candles)
    test.calculate()
    print(test.get_as_list())
    assert not deepdiff.DeepDiff(
        test.get_as_list()[-350:],
        expected_RSI[-350:],
        ignore_order=True,
        significant_digits=1,
    )
