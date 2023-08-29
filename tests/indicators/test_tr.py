import pytest
from hexital import TR


@pytest.mark.usefixtures("candles", "expected_TR")
def test_indicator(candles, expected_TR):
    test = TR(candles=candles)
    test.calculate()
    print(test.get_as_list())
    assert pytest.approx(test.get_as_list()) == expected_TR
