import deepdiff
import pytest
from hexital import TR


@pytest.mark.usefixtures("candles", "expected_TR")
def test_indicator(candles, expected_TR):
    test = TR(candles=candles)
    test.calculate()
    print(test.as_list)
    assert not deepdiff.DeepDiff(
        test.as_list,
        expected_TR,
        significant_digits=1,
    )
