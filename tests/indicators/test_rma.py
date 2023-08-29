import deepdiff
import pytest
from hexital import RMA


@pytest.mark.usefixtures("candles", "expected_RMA")
def test_indicator(candles, expected_RMA):
    test = RMA(candles=candles)
    test.calculate()
    assert not deepdiff.DeepDiff(
        test.get_as_list(),
        expected_RMA,
        ignore_order=True,
        significant_digits=1,
    )
