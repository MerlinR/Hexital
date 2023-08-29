import deepdiff
import pytest
from hexital import EMA


@pytest.mark.usefixtures("candles", "expected_EMA")
def test_indicator(candles, expected_EMA):
    test = EMA(candles=candles)
    test.calculate()
    assert not deepdiff.DeepDiff(
        test.as_list,
        expected_EMA,
        ignore_order=True,
        significant_digits=1,
    )
