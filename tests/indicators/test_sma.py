import pytest
from hexital import SMA


@pytest.mark.usefixtures("candles", "expected_SMA")
def test_indicator(candles, expected_SMA):
    test = SMA(candles=candles)
    test.calculate()
    print(test.get_as_list())
    assert pytest.approx(test.get_as_list()) == expected_SMA
