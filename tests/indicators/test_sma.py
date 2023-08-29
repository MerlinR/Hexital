import deepdiff
import pytest
from hexital import SMA


@pytest.mark.usefixtures("candles", "expected_SMA")
def test_indicator(candles, expected_SMA):
    test = SMA(candles=candles)
    test.calculate()
    print(test.get_as_list())
    assert not deepdiff.DeepDiff(
        test.get_as_list(),
        expected_SMA,
        ignore_order=True,
        significant_digits=1,
    )
