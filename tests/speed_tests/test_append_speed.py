import copy
import timeit
from functools import partial

import pytest
from hexital import EMA, OHLCV


@pytest.fixture(name="nasdaq_candles_large")
@pytest.mark.usefixtures("candles")
def fixture_nasdaq_data_large(candles):
    def duplicate(candles, number=2):
        i = 0
        out_candles = []
        for i in range(number):
            out_candles = out_candles + copy.deepcopy(candles)
        return out_candles

    return duplicate(candles, 178)


@pytest.fixture(name="nasdaq_candles_31st")
@pytest.mark.usefixtures("candles")
def fixture_nasdaq_data_31st(candles):
    return candles[30]


def test_data_timed(nasdaq_candles_large):
    test_count = 3

    # print(nasdaq_candles)
    def time_all(candles):
        new_candles = copy.deepcopy(candles)
        test = EMA(
            candles=new_candles,
            period=20,
            input_value="close",
        )
        test.calculate()

    full_calc = min(
        timeit.repeat(
            partial(time_all, nasdaq_candles_large), repeat=1, number=test_count
        )
    )

    print(f"Full_calc: {full_calc}s")
    assert True


def test_data_append_timed(nasdaq_candles_large, nasdaq_candles_31st):
    test_count = 3
    test = EMA(candles=nasdaq_candles_large, period=20, input_value="close")
    test.calculate()

    def time_append(candles, appender):
        candles.append(copy.deepcopy(appender))
        test.calculate()
        candles.pop()

    timed = min(
        timeit.repeat(
            partial(time_append, nasdaq_candles_large, nasdaq_candles_31st),
            repeat=1,
            number=test_count,
        )
    )

    print(f"Append_calc: {timed}s")
    assert True
