import deepdiff
import pytest
from hexital import RSI


@pytest.mark.usefixtures("candles", "expected_RSI")
def test_indicator(candles, expected_RSI):
    test = RSI(candles=candles)
    test.calculate()
    assert not deepdiff.DeepDiff(
        test.get_as_list(),
        expected_RSI,
        ignore_order=True,
        significant_digits=1,
    )
