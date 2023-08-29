import deepdiff
import pytest
from hexital import SMA


@pytest.mark.usefixtures("candles", "expected_SMA")
def test_indicator(candles, expected_SMA):
    test = SMA(candles=candles)
    test.calculate()
    print(test.as_list)
    assert not deepdiff.DeepDiff(
        test.as_list,
        expected_SMA,
        significant_digits=1,
    )
