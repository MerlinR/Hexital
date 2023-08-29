import deepdiff
import pytest
from hexital import TR


@pytest.mark.usefixtures("candles", "expected_TR")
def test_indicator(candles, expected_TR):
    test = TR(candles=candles)
    test.calculate()
    print(test.get_as_list())
    assert not deepdiff.DeepDiff(
        test.get_as_list(),
        expected_TR,
        ignore_order=True,
        significant_digits=1,
    )
