import pytest
from hexital import TR


@pytest.mark.usefixtures("candles", "expected_TR")
def test_indicator(candles, expected_TR):
    test = TR(candles=candles)
    test.calculate()
    # print(test.get_as_list())
    assert test.get_as_list()[-499:] == expected_TR[-499:]
