import deepdiff
import pytest
from hexital import RMA


@pytest.mark.usefixtures("candles", "expected_RMA")
def test_indicator(candles, expected_RMA):
    test = RMA(candles=candles)
    test.calculate()
    print(test.get_as_list())
    assert not deepdiff.DeepDiff(
        test.get_as_list()[-400:],
        expected_RMA[-400:],
        ignore_order=True,
        significant_digits=1,
    )
