import pytest
from hexital import EMA


@pytest.mark.usefixtures("candles", "expected_EMA")
def test_indicator(candles, expected_EMA):
    test = EMA(candles=candles)
    test.calculate()
    print(test.get_as_list())
    assert pytest.approx(test.get_as_list()) == expected_EMA
