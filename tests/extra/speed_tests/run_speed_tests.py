import random
import time
from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd
import pandas_ta as ta
from hexital import Candle, Hexital

PATH = "tests/extra/speed_tests/"


def generate_random_candles(count: int) -> list:
    data = []

    for i in range(count):
        data.append(
            {
                "open": random.randint(0, 9000000),
                "high": random.randint(0, 9000000),
                "low": random.randint(0, 9000000),
                "close": random.randint(0, 9000000),
                "volume": random.randint(0, 10000),
                "timestamp": datetime.fromtimestamp(i),
            },
        )

    return data


def add_timestamp(candles: pd.DataFrame):
    candles["timestamp"] = pd.date_range(
        start=datetime(2032, 1, 1), periods=candles.shape[0], freq="min"
    )
    candles.set_index(pd.DatetimeIndex(candles["timestamp"]), inplace=True)
    return candles.drop("timestamp", axis=1)


def create_graph(data: dict, title: str):
    for key, val in data.items():
        if key == "count":
            continue
        plt.plot(data["count"], val, label=key)

    plt.xlabel("Candles Count")
    plt.ylabel("Time (Seconds)")

    plt.title(title)
    plt.legend()

    plt.savefig(f"{PATH}/{title}.png")


def test_pandas_ta_bulk(candle_length: int, strat: list):
    df = pd.DataFrame.from_dict(generate_random_candles(candle_length))
    df.set_index("timestamp", inplace=True)

    MyStrategy = ta.Strategy(
        name="Truth Source",
        ta=strat,
    )
    start_time = time.time()
    df.ta.strategy(MyStrategy)
    return time.time() - start_time


def test_pandas_ta_incremental(candle_length: int, strat: list):
    df = pd.DataFrame.from_dict(generate_random_candles(candle_length))
    df.set_index("timestamp", inplace=True)

    MyStrategy = ta.Strategy(
        name="Truth Source",
        ta=strat,
    )
    used_df = pd.DataFrame([df.iloc[0]])

    start_time = time.time()
    for i in range(1, len(df.index)):
        used_df.ta.strategy(MyStrategy)
        used_df = pd.concat([used_df, pd.DataFrame([df.iloc[i]])])
    return time.time() - start_time


def test_hexital_bulk(candle_length: int, strat: list):
    hexitl = Hexital("test", Candle.from_dicts(generate_random_candles(candle_length)), strat)
    start_time = time.time()
    hexitl.calculate()
    return time.time() - start_time


def hexital_incremental(candle_length: int, strat: list):
    candles = Candle.from_dicts(generate_random_candles(candle_length))

    hexitl = Hexital("Test Stratergy", [candles[0]], strat)
    start_time = time.time()
    for i in range(1, len(candles)):
        hexitl.calculate()
        hexitl.append(candles[i])
    return time.time() - start_time


def run_test_ema(candle_count: int, steps: int):
    hex_strat = [{"indicator": "EMA"}]
    pd_strat = [{"kind": "ema"}]
    results = {
        "count": [],
        "Hexital Bulk": [],
        "Hexital Incremental": [],
        "Pandas_TA Bulk": [],
        "Pandas_TA Incremental": [],
    }

    for i in range(0, candle_count, steps):
        if i == 0:
            continue
        print(f"Candles: {i}")
        results["count"].append(i)
        hb1 = test_hexital_bulk(i, hex_strat)
        hb2 = test_hexital_bulk(i, hex_strat)
        results["Hexital Bulk"].append(round((hb1 + hb2) / 2, 4))

        hi1 = hexital_incremental(i, hex_strat)
        hi2 = hexital_incremental(i, hex_strat)
        results["Hexital Incremental"].append(round((hi1 + hi2) / 2, 4))

        pb1 = test_pandas_ta_bulk(i, pd_strat)
        pb2 = test_pandas_ta_bulk(i, pd_strat)
        results["Pandas_TA Bulk"].append(round((pb1 + pb2) / 2, 4))

        pi1 = test_pandas_ta_incremental(i, pd_strat)
        pi2 = test_pandas_ta_incremental(i, pd_strat)
        results["Pandas_TA Incremental"].append(round((pi1 + pi2) / 2, 4))
        print(f"Time: {results['Pandas_TA Incremental'][-1]}")

    create_graph(results, "EMA_10")


def run_test_supertrend(candle_count: int, steps: int):
    hex_strat = [{"indicator": "Supertrend"}]
    pd_strat = [{"kind": "supertrend"}]
    results = {
        "count": [],
        "Hexital Bulk": [],
        "Hexital Incremental": [],
        "Pandas_TA Bulk": [],
        "Pandas_TA Incremental": [],
    }

    for i in range(0, candle_count, steps):
        if i == 0:
            continue
        print(f"Candles: {i}")
        results["count"].append(i)
        hb1 = test_hexital_bulk(i, hex_strat)
        hb2 = test_hexital_bulk(i, hex_strat)
        results["Hexital Bulk"].append(round((hb1 + hb2) / 2, 4))

        hi1 = hexital_incremental(i, hex_strat)
        hi2 = hexital_incremental(i, hex_strat)
        results["Hexital Incremental"].append(round((hi1 + hi2) / 2, 4))

        pb1 = test_pandas_ta_bulk(i, pd_strat)
        pb2 = test_pandas_ta_bulk(i, pd_strat)
        results["Pandas_TA Bulk"].append(round((pb1 + pb2) / 2, 4))

        pi1 = test_pandas_ta_incremental(i, pd_strat)
        pi2 = test_pandas_ta_incremental(i, pd_strat)
        results["Pandas_TA Incremental"].append(round((pi1 + pi2) / 2, 4))

    create_graph(results, "Supertrend_7")


def run_test_macd_bulk_only(candle_count: int, steps: int, smooth: int):
    hex_strat = [{"indicator": "MACD"}]
    pd_strat = [{"kind": "macd"}]
    results = {
        "count": [],
        "Hexital Bulk": [],
        "Pandas_TA Bulk": [],
    }

    for i in range(0, candle_count, steps):
        if i == 0:
            continue
        print(f"Candles: {i}")
        results["count"].append(i)

        vals = 0
        for idx in range(smooth):
            vals += test_hexital_bulk(i, hex_strat)

        results["Hexital Bulk"].append(round(vals / smooth, 4))

        vals = 0
        for idx in range(smooth):
            vals += test_pandas_ta_bulk(i, pd_strat)

        results["Pandas_TA Bulk"].append(round(vals / smooth, 4))

    create_graph(results, "MACD_26_12 Bulk Calculations")


def run_test_real_usage(candle_count: int, steps: int):
    hex_strat = [{"indicator": "MACD"}]
    pd_strat = [{"kind": "macd"}]
    results = {
        "count": [],
        "Hexital Incremental": [],
        "Pandas_TA Incremental": [],
    }

    for i in range(0, candle_count, steps):
        if i == 0:
            continue
        print(f"Candles: {i}")
        results["count"].append(i)

        candles = Candle.from_dicts(generate_random_candles(i))
        hexitl = Hexital("Test Stratergy", candles, hex_strat)
        hexitl.calculate()
        start_time = time.time()
        hexitl.append(Candle.from_dict(generate_random_candles(1)[0]))
        hexitl.calculate()
        results["Hexital Incremental"].append(round(time.time() - start_time, 4))

        df = pd.DataFrame.from_dict(generate_random_candles(i))
        df.set_index("timestamp", inplace=True)

        MyStrategy = ta.Strategy(
            name="Truth Source",
            ta=pd_strat,
        )
        df.ta.strategy(MyStrategy)

        start_time = time.time()
        df = pd.concat([df, pd.DataFrame.from_dict(generate_random_candles(1))])
        df.ta.strategy(MyStrategy)
        results["Pandas_TA Incremental"].append(round(time.time() - start_time, 4))

    for key, val in results.items():
        if key == "count":
            continue
        plt.plot(results["count"], val, label=key)

    plt.xlabel("Adding n Candle")
    plt.ylabel("Time (Seconds)")

    plt.title("MACD_26_12 Real World Incremental Usage")
    plt.legend()

    plt.savefig(f"{PATH}/MACD_26_12_real_world.png")


def run_tests():
    steps = 10
    run_test_ema(500, steps)
    run_test_supertrend(500, steps)
    run_test_macd_bulk_only(10000, steps, 6)
    run_test_real_usage(10000, steps)


if __name__ == "__main__":
    run_tests()
