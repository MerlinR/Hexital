import copy
import csv
import timeit
from datetime import datetime
from functools import partial

import pytest
from hexital import EMA, Candle


@pytest.fixture(name="nasdaq_candles")
def fixture_nasdaq_data():
    candles = []
    with open("tests/data/NASDAQ.csv", newline="") as csvfile:
        index = csv.reader(csvfile, delimiter=",")
        for row in index:
            if row[0] == "Date":
                continue
            candles.append(
                Candle(
                    open=float(row[1]),
                    high=float(row[2]),
                    low=float(row[3]),
                    close=float(row[4]),
                    volume=int(row[6]),
                )
            )
    return candles


@pytest.fixture(name="nasdaq_candles_large")
def fixture_nasdaq_data_large(nasdaq_candles):
    def duplicate(candles, number=2):
        i = 0
        out_candles = []
        for i in range(number):
            out_candles = out_candles + copy.deepcopy(candles)
        return out_candles

    return duplicate(nasdaq_candles, 178)


@pytest.fixture(name="nasdaq_candles_10")
def fixture_nasdaq_data_10(nasdaq_candles):
    return nasdaq_candles[0:10]


@pytest.fixture(name="nasdaq_candles_11th")
def fixture_nasdaq_data_11th(nasdaq_candles):
    return nasdaq_candles[10]


def test_data(nasdaq_candles_10):
    # print(nasdaq_candles)
    test = EMA(candles=nasdaq_candles_10, period=5, input_value="close")
    # print(len(nasdaq_candles_10))
    # for item in nasdaq_candles_10:
    #     print(item.close)
    #     print(item.technical_indicators)
    # print(",".join([str(item.close) for item in nasdaq_candles_10]))
    assert False


def test_data_append(nasdaq_candles_10, nasdaq_candles_11th):
    # print(nasdaq_candles)
    candles = nasdaq_candles_10
    test = EMA(candles=candles, period=5, input_value="close")
    candles.append(nasdaq_candles_11th)
    test.calculate()
    # print(len(candles))
    # for item in candles:
    #     print(item.close)
    #     print(item.technical_indicators)
    # print(",".join([str(item.close) for item in candles]))
    assert False


def test_data_timed(nasdaq_candles_large):
    test_count = 5

    # print(nasdaq_candles)
    def time_all(candles):
        new_candles = copy.deepcopy(candles)
        test = EMA(
            candles=new_candles,
            period=20,
            input_value="close",
        )

    full_calc = min(
        timeit.repeat(
            partial(time_all, nasdaq_candles_large), repeat=1, number=test_count
        )
    )

    print(f"Full_calc: {full_calc}s")
    assert False


def test_data_append_timed(nasdaq_candles_large, nasdaq_candles_11th):
    test_count = 5
    test = EMA(candles=nasdaq_candles_large, period=20, input_value="close")

    def time_append(candles, appender):
        candles.append(copy.deepcopy(appender))
        test.calculate()
        candles.pop()

    timed = min(
        timeit.repeat(
            partial(time_append, nasdaq_candles_large, nasdaq_candles_11th),
            repeat=1,
            number=test_count,
        )
    )

    print(f"Append_calc: {timed}s")
    assert False
