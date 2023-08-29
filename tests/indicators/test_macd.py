import deepdiff
import pytest
from hexital import MACD


@pytest.mark.usefixtures("candles", "expected_MACD")
def test_indicator(candles, expected_MACD):
    test = MACD(candles=candles)
    test.calculate()
    print(len(expected_MACD))

    assert not deepdiff.DeepDiff(
        test.as_list,
        expected_MACD,
        ignore_order=True,
        significant_digits=1,
    )
