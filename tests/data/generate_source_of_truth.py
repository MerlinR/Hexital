import json
from datetime import datetime
from typing import Dict

import numpy as np
import pandas as pd
import pandas_ta as ta


def load_json_candles() -> list:
    csv_file = open("tests/data/test_candles.json")
    return json.load(csv_file)


def save_json_result(data: list, filename: str):
    with open(f"tests/data/source_of_truth/{filename}.json", "w") as json_file:
        json.dump(
            data,
            json_file,
            indent=4,
        )


def add_timestamp(candles: pd.DataFrame):
    candles["timestamp"] = pd.date_range(
        start=datetime(2032, 1, 1), periods=candles.shape[0], freq="min"
    )
    candles.set_index(pd.DatetimeIndex(candles["timestamp"]), inplace=True)
    return candles.drop("timestamp", axis=1)


def round_values(values: float | Dict[str, float]) -> float | Dict[str, float]:
    if isinstance(values, dict):
        for key, val in values.items():
            if val is not None:
                values[key] = round(val, 4)
    elif isinstance(values, float):
        values = round(values, 4)

    return values


def generate():
    df = pd.DataFrame.from_dict(load_json_candles())
    df = add_timestamp(df)

    MyStrategy = ta.Strategy(
        name="Truth Source",
        ta=[
            {"kind": "true_range"},
            {"kind": "rma"},
            {"kind": "sma"},
            {"kind": "sma", "length": 3},
            {"kind": "ema"},
            {"kind": "macd"},
            {"kind": "rsi"},
            {"kind": "atr"},
            {"kind": "atr", "length": 20},
            {"kind": "stoch"},
            {"kind": "supertrend"},
            {"kind": "wma"},
            {"kind": "vwma"},
            {"kind": "vwap"},
            {"kind": "obv"},
            {"kind": "kc"},
            {"kind": "hl2"},
        ],
    )

    df.ta.strategy(MyStrategy)
    df = df.astype(object).replace(np.nan, None)

    for col in df.columns:
        if col in ["open", "high", "low", "close", "volume"]:
            continue
        print(f"Generated: {col}")

    save_json_result([round_values(value) for value in df["RMA_10"].tolist()], "RMA")
    save_json_result([round_values(value) for value in df["TRUERANGE_1"].tolist()], "TR")
    save_json_result([round_values(value) for value in df["EMA_10"].tolist()], "EMA")
    save_json_result([round_values(value) for value in df["SMA_10"].tolist()], "SMA")
    save_json_result([round_values(value) for value in df["SMA_3"].tolist()], "SMA_3")
    save_json_result([round_values(value) for value in df["RSI_14"].tolist()], "RSI")
    save_json_result([round_values(value) for value in df["ATRr_14"].tolist()], "ATR")
    save_json_result([round_values(value) for value in df["WMA_10"].tolist()], "WMA")
    save_json_result([round_values(value) for value in df["VWMA_10"].tolist()], "VWMA")
    save_json_result([round_values(value) for value in df["VWAP_D"].tolist()], "VWAP")
    save_json_result([round_values(value) for value in df["OBV"].tolist()], "OBV")
    save_json_result([round_values(value) for value in df["HL2"].tolist()], "HL2")

    kc_l = [round_values(value) for value in df["KCLe_20_2"].tolist()]
    kc_b = [round_values(value) for value in df["KCBe_20_2"].tolist()]
    kc_u = [round_values(value) for value in df["KCUe_20_2"].tolist()]
    kc_data = []
    for kc in zip(kc_l, kc_b, kc_u):
        kc_data.append({"lower": kc[0], "band": kc[1], "upper": kc[2]})
    save_json_result(kc_data, "KC")
    save_json_result([round_values(value) for value in df["ATRr_20"].tolist()], "ATR_20")

    stochk = [round_values(value) for value in df["STOCHk_14_3_3"].tolist()]
    stochd = [round_values(value) for value in df["STOCHd_14_3_3"].tolist()]
    stoch_data = []
    for stoch in zip(stochk, stochd):
        stoch_data.append({"k": stoch[0], "d": stoch[1]})
    save_json_result(stoch_data, "STOCH")

    macd = [round_values(value) for value in df["MACD_12_26_9"].tolist()]
    macd_h = [round_values(value) for value in df["MACDh_12_26_9"].tolist()]
    macd_s = [round_values(value) for value in df["MACDs_12_26_9"].tolist()]
    macd_data = []
    for macd in zip(macd, macd_s, macd_h):
        macd_data.append({"MACD": macd[0], "signal": macd[1], "histogram": macd[2]})
    save_json_result(macd_data, "MACD")

    supertrend = [round_values(value) for value in df["SUPERT_7_3.0"].tolist()]
    supertrendd = [round_values(value) for value in df["SUPERTd_7_3.0"].tolist()]
    supertrendl = [round_values(value) for value in df["SUPERTl_7_3.0"].tolist()]
    supertrends = [round_values(value) for value in df["SUPERTs_7_3.0"].tolist()]
    supertrend_data = []
    for trend in zip(supertrend, supertrendd, supertrendl, supertrends):
        supertrend_data.append(
            {
                "trend": trend[0],
                "direction": trend[1],
                "long": trend[2],
                "short": trend[3],
            }
        )
    save_json_result(supertrend_data, "SUPERTREND")


if __name__ == "__main__":
    generate()
