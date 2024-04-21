import json
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
import pandas_ta as ta

PATH_INDICATOR = "source_of_truth/indicators"
PATH_PATTERN = "source_of_truth/pattern"
PATH_CANDLES = "source_of_truth/candles"
PATH_DATA = "."


def load_json_candles() -> List[dict]:
    csv_file = open("tests/data/test_candles.json")
    return json.load(csv_file)


def save_json_result(data: list, filename: str, path: Optional[str] = None):
    path = path if path is not None else PATH_INDICATOR
    with open(f"tests/data/{path}/{filename}.json", "w") as json_file:
        json.dump(data, json_file, indent=4, default=str)


def round_values(values: float | Dict[str, float]) -> float | Dict[str, float]:
    if isinstance(values, dict):
        for key, val in values.items():
            if val is not None:
                values[key] = round(val, 4)
    elif isinstance(values, float):
        values = round(values, 4)

    return values


def print_new(df: pd.DataFrame):
    for col in df.columns:
        if col in ["open", "high", "low", "close", "volume", "timestamp"]:
            continue
        print(f"Column: {col}")


def candle_compress_dataframe(data: pd.DataFrame, freq: str = "5min"):
    data.set_index(pd.DatetimeIndex(data["timestamp"]), inplace=True)
    data.drop("timestamp", axis=1, inplace=True)

    ohlc_dict = {
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "volume": "sum",
    }

    for col in data.columns:
        if col not in ohlc_dict:
            ohlc_dict[col] = "last"

    data = data.resample(freq, closed="right", label="right").apply(ohlc_dict)
    return data


def generate_indicators():
    print("Generating Indicators")
    df = pd.DataFrame.from_dict(load_json_candles())
    df.set_index(pd.DatetimeIndex(df["timestamp"]), inplace=True)

    MyStrategy = ta.Strategy(
        name="Truth Source",
        ta=[
            {"kind": "true_range"},
            {"kind": "rma"},
            {"kind": "rma", "length": 20},
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
            {"kind": "roc"},
            {"kind": "adx"},
            {"kind": "hma"},
            {"kind": "stdev"},
            {"kind": "tsi"},
            {"kind": "bbands"},
            {"kind": "aroon"},
            {"kind": "donchian"},
        ],
    )

    df.ta.strategy(MyStrategy)
    df = df.astype(object).replace(np.nan, None)

    print_new(df)

    save_json_result([round_values(value) for value in df["RMA_10"].tolist()], "RMA")
    save_json_result([round_values(value) for value in df["RMA_20"].tolist()], "RMA_20")
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
    save_json_result([round_values(value) for value in df["ROC_10"].tolist()], "ROC")
    save_json_result([round_values(value) for value in df["ATRr_20"].tolist()], "ATR_20")
    save_json_result([round_values(value) for value in df["HMA_10"].tolist()], "HMA")
    save_json_result([round_values(value) for value in df["STDEV_30"].tolist()], "STDEV")
    save_json_result([round_values(value) for value in df["TSI_13_25_13"].tolist()], "TSI")

    kc_data = []
    for kc in zip(
        [round_values(value) for value in df["KCLe_20_2"].tolist()],
        [round_values(value) for value in df["KCBe_20_2"].tolist()],
        [round_values(value) for value in df["KCUe_20_2"].tolist()],
    ):
        kc_data.append({"lower": kc[0], "band": kc[1], "upper": kc[2]})
    save_json_result(kc_data, "KC")

    stoch_data = []
    for stoch in zip(
        [round_values(value) for value in df["STOCHk_14_3_3"].tolist()],
        [round_values(value) for value in df["STOCHd_14_3_3"].tolist()],
    ):
        stoch_data.append({"k": stoch[0], "d": stoch[1]})
    save_json_result(stoch_data, "STOCH")

    macd_data = []
    for macd in zip(
        [round_values(value) for value in df["MACD_12_26_9"].tolist()],
        [round_values(value) for value in df["MACDs_12_26_9"].tolist()],
        [round_values(value) for value in df["MACDh_12_26_9"].tolist()],
    ):
        macd_data.append({"MACD": macd[0], "signal": macd[1], "histogram": macd[2]})
    save_json_result(macd_data, "MACD")

    supertrend_data = []
    for trend in zip(
        [round_values(value) for value in df["SUPERT_7_3.0"].tolist()],
        [round_values(value) for value in df["SUPERTd_7_3.0"].tolist()],
        [round_values(value) for value in df["SUPERTl_7_3.0"].tolist()],
        [round_values(value) for value in df["SUPERTs_7_3.0"].tolist()],
    ):
        supertrend_data.append(
            {
                "trend": trend[0],
                "direction": trend[1],
                "long": trend[2],
                "short": trend[3],
            }
        )
    save_json_result(supertrend_data, "SUPERTREND")

    adx_data = []
    for adx_row in zip(
        [round_values(value) for value in df["ADX_14"].tolist()],
        [round_values(value) for value in df["DMP_14"].tolist()],
        [round_values(value) for value in df["DMN_14"].tolist()],
    ):
        adx_data.append({"ADX": adx_row[0], "DM_Plus": adx_row[1], "DM_Neg": adx_row[2]})
    save_json_result(adx_data, "ADX")

    bbands_data = []
    for bbands_row in zip(
        [round_values(value) for value in df["BBL_5_2.0"].tolist()],
        [round_values(value) for value in df["BBM_5_2.0"].tolist()],
        [round_values(value) for value in df["BBU_5_2.0"].tolist()],
    ):
        bbands_data.append(
            {
                "BBL": bbands_row[0],
                "BBM": bbands_row[1],
                "BBU": bbands_row[2],
            }
        )
    save_json_result(bbands_data, "BBANDS")

    aroon_data = []
    for aroon_row in zip(
        [round_values(value) for value in df["AROONU_14"].tolist()],
        [round_values(value) for value in df["AROOND_14"].tolist()],
        [round_values(value) for value in df["AROONOSC_14"].tolist()],
    ):
        aroon_data.append(
            {"AROONU": aroon_row[0], "AROOND": aroon_row[1], "AROONOSC": aroon_row[2]}
        )
    save_json_result(aroon_data, "AROON")

    donchian_data = []
    for donchian_row in zip(
        [round_values(value) for value in df["DCL_20_20"].tolist()],
        [round_values(value) for value in df["DCM_20_20"].tolist()],
        [round_values(value) for value in df["DCU_20_20"].tolist()],
    ):
        donchian_data.append(
            {"DCL": donchian_row[0], "DCM": donchian_row[1], "DCU": donchian_row[2]}
        )
    save_json_result(donchian_data, "DONCHIAN")


def generate_indicators_timeframe(frame: str):
    print(f"Generating Indicators with timeframe: {frame}")
    df = pd.DataFrame.from_dict(load_json_candles())
    df = candle_compress_dataframe(df, frame)

    MyStrategy = ta.Strategy(
        name="Truth Source",
        ta=[
            {"kind": "ema"},
            {"kind": "sma"},
            {"kind": "obv"},
        ],
    )

    df.ta.strategy(MyStrategy)
    df = df.astype(object).replace(np.nan, None)

    print_new(df)
    frame = frame.replace("min", "T")
    save_json_result([round_values(value) for value in df["EMA_10"].tolist()], f"EMA_{frame}")
    save_json_result([round_values(value) for value in df["SMA_10"].tolist()], f"SMA_{frame}")
    save_json_result([round_values(value) for value in df["OBV"].tolist()], f"OBV_{frame}")


def generate_patterns():
    print("Generating Patterns")
    df = pd.DataFrame.from_dict(load_json_candles())

    df = df.ta.cdl_pattern(
        name=[
            "doji",
            "dojistar",
            "hammer",
            "invertedhammer",
        ]
    )
    df = df.astype(object).replace(np.nan, None)

    print_new(df)

    save_json_result(
        [bool(value) for value in df["CDL_DOJI_10_0.1"].tolist()], "DOJI", PATH_PATTERN
    )
    save_json_result(
        [bool(value) for value in df["CDL_DOJISTAR"].tolist()], "DOJISTAR", PATH_PATTERN
    )
    save_json_result([bool(value) for value in df["CDL_HAMMER"].tolist()], "HAMMER", PATH_PATTERN)
    save_json_result(
        [bool(value) for value in df["CDL_INVERTEDHAMMER"].tolist()],
        "INVERTEDHAMMER",
        PATH_PATTERN,
    )


def generate_heikin_candles():
    print("Generating Candles")
    df = pd.DataFrame.from_dict(load_json_candles())

    dfha = ta.ha(df["open"], df["high"], df["low"], df["close"])
    df = pd.merge(df, dfha, right_index=True, left_index=True)
    df = df.astype(object).replace(np.nan, None)
    print_new(df)

    df.drop(columns=["open", "high", "low", "close"], axis=1, inplace=True)
    df.rename(
        columns={
            "HA_open": "open",
            "HA_high": "high",
            "HA_low": "low",
            "HA_close": "close",
        },
        inplace=True,
    )

    save_json_result(df.to_dict("records"), "test_candles_heikin_ashi", PATH_CANDLES)


def generate_timeframe_candles(frame: str):
    print(f"Generating candles with timeframe: {frame}")
    df = pd.DataFrame.from_dict(load_json_candles())
    df = candle_compress_dataframe(df, frame)
    df = df.astype(object).replace(np.nan, None)

    df["timestamp"] = df.index

    output = []
    for row in df.to_dict("records"):
        row["timestamp"] = row["timestamp"].to_pydatetime().isoformat(timespec="seconds")
        output.append(row)

    save_json_result(output, f"test_candles_{frame.replace('min','T')}", PATH_CANDLES)


if __name__ == "__main__":
    generate_indicators()
    generate_indicators_timeframe("5min")
    generate_indicators_timeframe("10min")
    generate_patterns()
    generate_timeframe_candles("5min")
    generate_timeframe_candles("10min")
    generate_heikin_candles()
