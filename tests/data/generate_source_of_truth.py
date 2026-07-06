import json

import numpy as np
import pandas as pd
import pandas_ta as ta

PATH_INDICATOR = "source_of_truth/indicators"
PATH_PATTERN = "source_of_truth/pattern"
PATH_CANDLES = "source_of_truth/candles"
PATH_DATA = "."


def load_json_candles() -> list[dict]:
    csv_file = open("tests/data/test_candles.json")
    return json.load(csv_file)


def save_as_json(data: list, filename: str, path: str | None = None):
    path = path if path is not None else PATH_INDICATOR
    with open(f"tests/data/{path}/{filename}.json", "w") as json_file:
        json.dump(data, json_file, indent=4, default=str)


def save_structured_result(
    df: pd.DataFrame,
    filename: str,
    columns: list[tuple[str, str]],
    path: str | None = None,
) -> None:
    rounded_columns = [
        [round_values(value) for value in df[column_name].tolist()]
        for column_name, _ in columns
    ]
    data = [
        {output_key: value for value, (_, output_key) in zip(row, columns)}
        for row in zip(*rounded_columns)
    ]
    save_as_json(data, filename, path)


def round_values(values: float | dict[str, float]) -> float | dict[str, float]:
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
            {"kind": "dema"},
            {"kind": "ema"},
            {"kind": "macd"},
            {"kind": "rsi"},
            {"kind": "atr"},
            {"kind": "natr"},
            {"kind": "atr", "length": 20},
            {"kind": "stoch"},
            {"kind": "supertrend"},
            {"kind": "tema"},
            {"kind": "wma"},
            {"kind": "vwma"},
            {"kind": "vwap"},
            {"kind": "vwap", "anchor": "1h"},
            {"kind": "obv"},
            {"kind": "kc"},
            {"kind": "hl2"},
            {"kind": "hlc3"},
            {"kind": "roc"},
            {"kind": "adx"},
            {"kind": "hma"},
            {"kind": "stdev"},
            {"kind": "trix"},
            {"kind": "tsi"},
            {"kind": "uo"},
            {"kind": "bbands"},
            {"kind": "aroon"},
            {"kind": "donchian"},
            {"kind": "cmo"},
            {"kind": "mfi"},
            {"kind": "midpoint"},
            {"kind": "jma"},
            {"kind": "jma", "length": 10, "phase": 80.0},
            {"kind": "kama"},
            {"kind": "rvi"},
            {"kind": "squeeze"},
            {"kind": "squeeze_pro"},
            {"kind": "zscore"},
            {"kind": "cci"},
            {"kind": "willr"},
            {"kind": "ppo"},
            {"kind": "psar"},
            {"kind": "ichimoku"},
        ],
    )

    df.ta.strategy(MyStrategy)
    df = df.astype(object).replace(np.nan, None)

    print_new(df)

    save_as_json([round_values(value) for value in df["RMA_10"].tolist()], "RMA")
    save_as_json([round_values(value) for value in df["RMA_20"].tolist()], "RMA_20")
    save_as_json([round_values(value) for value in df["TRUERANGE_1"].tolist()], "TR")
    save_as_json([round_values(value) for value in df["DEMA_10"].tolist()], "DEMA")
    save_as_json([round_values(value) for value in df["EMA_10"].tolist()], "EMA")
    save_as_json([round_values(value) for value in df["SMA_10"].tolist()], "SMA")
    save_as_json([round_values(value) for value in df["SMA_3"].tolist()], "SMA_3")
    save_as_json([round_values(value) for value in df["RSI_14"].tolist()], "RSI")
    save_as_json([round_values(value) for value in df["ATRr_14"].tolist()], "ATR")
    save_as_json([round_values(value) for value in df["NATR_14"].tolist()], "NATR")
    save_as_json([round_values(value) for value in df["TEMA_10"].tolist()], "TEMA")
    save_as_json([round_values(value) for value in df["WMA_10"].tolist()], "WMA")
    save_as_json([round_values(value) for value in df["VWMA_10"].tolist()], "VWMA")
    save_as_json([round_values(value) for value in df["VWAP_D"].tolist()], "VWAP")
    save_as_json([round_values(value) for value in df["VWAP_1H"].tolist()], "VWAP_H1")
    save_as_json([round_values(value) for value in df["OBV"].tolist()], "OBV")
    save_as_json([round_values(value) for value in df["HL2"].tolist()], "HL2")
    save_as_json([round_values(value) for value in df["HLC3"].tolist()], "HLC")
    save_as_json([round_values(value) for value in df["ROC_10"].tolist()], "ROC")
    save_as_json([round_values(value) for value in df["ATRr_20"].tolist()], "ATR_20")
    save_as_json([round_values(value) for value in df["HMA_10"].tolist()], "HMA")
    save_as_json([round_values(value) for value in df["STDEV_30"].tolist()], "STDEV")
    save_structured_result(
        df,
        "TRIX",
        [
            ("TRIX_30_9", "TRIX"),
            ("TRIXs_30_9", "signal"),
        ],
    )
    save_as_json([round_values(value) for value in df["TSI_13_25_13"].tolist()], "TSI")
    save_as_json([round_values(value) for value in df["UO_7_14_28"].tolist()], "UO")
    save_as_json([round_values(value) for value in df["BBB_5_2.0"].tolist()], "BANDWIDTH")
    save_as_json([round_values(value) for value in df["CMO_14"].tolist()], "CMO")
    save_as_json([round_values(value) for value in df["MFI_14"].tolist()], "MFI")
    save_as_json([round_values(value) for value in df["MIDPOINT_2"].tolist()], "MIDPOINT")
    save_as_json([round_values(value) for value in df["JMA_7_0"].tolist()], "JMA")
    save_as_json(
        [round_values(value) for value in df["JMA_10_80.0"].tolist()], "JMA_extra"
    )
    save_as_json([round_values(value) for value in df["KAMA_10_2_30"].tolist()], "KAMA")
    save_as_json([round_values(value) for value in df["RVI_14"].tolist()], "RVI")
    save_as_json([round_values(value) for value in df["ZS_30"].tolist()], "ZSCORE")
    save_as_json([round_values(value) for value in df["CCI_14_0.015"].tolist()], "CCI")
    save_as_json([round_values(value) for value in df["WILLR_14"].tolist()], "WILLR")
    chandelier_atr = ta.atr(df["high"], df["low"], df["close"], length=22)
    chandelier_df = pd.DataFrame(
        {
            "long": df["high"].rolling(22).max() - (3.0 * chandelier_atr),
            "short": df["low"].rolling(22).min() + (3.0 * chandelier_atr),
        }
    )
    chandelier_df = chandelier_df.astype(object).replace(np.nan, None)
    save_structured_result(
        chandelier_df,
        "CHANDELIEREXIT",
        [
            ("long", "long"),
            ("short", "short"),
        ],
    )

    save_structured_result(
        df,
        "KC",
        [
            ("KCLe_20_2", "lower"),
            ("KCBe_20_2", "band"),
            ("KCUe_20_2", "upper"),
        ],
    )
    save_structured_result(
        df,
        "STOCH",
        [
            ("STOCHk_14_3_3", "k"),
            ("STOCHd_14_3_3", "d"),
        ],
    )
    save_structured_result(
        df,
        "MACD",
        [
            ("MACD_12_26_9", "MACD"),
            ("MACDs_12_26_9", "signal"),
            ("MACDh_12_26_9", "histogram"),
        ],
    )
    save_structured_result(
        df,
        "SUPERTREND",
        [
            ("SUPERT_7_3.0", "trend"),
            ("SUPERTd_7_3.0", "direction"),
            ("SUPERTl_7_3.0", "long"),
            ("SUPERTs_7_3.0", "short"),
        ],
    )
    save_structured_result(
        df,
        "ADX",
        [
            ("ADX_14", "ADX"),
            ("DMP_14", "DM_Plus"),
            ("DMN_14", "DM_Neg"),
        ],
    )
    save_structured_result(
        df,
        "BBANDS",
        [
            ("BBL_5_2.0", "BBL"),
            ("BBM_5_2.0", "BBM"),
            ("BBU_5_2.0", "BBU"),
        ],
    )
    save_structured_result(
        df,
        "AROON",
        [
            ("AROONU_14", "AROONU"),
            ("AROOND_14", "AROOND"),
            ("AROONOSC_14", "AROONOSC"),
        ],
    )
    save_structured_result(
        df,
        "DONCHIAN",
        [
            ("DCL_20_20", "DCL"),
            ("DCM_20_20", "DCM"),
            ("DCU_20_20", "DCU"),
        ],
    )
    save_structured_result(
        df,
        "SQUEEZE",
        [
            ("SQZ_20_2.0_20_1.5", "SQZ"),
            ("SQZ_ON", "ON"),
            ("SQZ_OFF", "OFF"),
        ],
    )
    save_structured_result(
        df,
        "SQUEEZE_PRO",
        [
            ("SQZPRO_20_2.0_20_2_1.5_1", "SQZ"),
            ("SQZPRO_ON_WIDE", "Wide"),
            ("SQZPRO_ON_NORMAL", "Normal"),
            ("SQZPRO_ON_NARROW", "Narrow"),
            ("SQZPRO_OFF", "OFF"),
        ],
    )
    save_structured_result(
        df,
        "PPO",
        [
            ("PPO_12_26_9", "PPO"),
            ("PPOh_12_26_9", "Histogram"),
            ("PPOs_12_26_9", "Signal"),
        ],
    )
    save_structured_result(
        df,
        "PSAR",
        [
            ("PSARl_0.02_0.2", "Long"),
            ("PSARs_0.02_0.2", "Short"),
            ("PSARaf_0.02_0.2", "Acceleration"),
            ("PSARr_0.02_0.2", "Reversal"),
        ],
    )
    save_structured_result(
        df,
        "ICHIMOKU",
        [
            ("ISA_9", "Lead_A"),
            ("ISB_26", "Lead_B"),
            ("ITS_9", "Conversion"),
            ("IKS_26", "Base"),
            ("ICS_26", "Span"),
        ],
    )


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
    save_as_json([round_values(value) for value in df["EMA_10"].tolist()], f"EMA_{frame}")
    save_as_json([round_values(value) for value in df["SMA_10"].tolist()], f"SMA_{frame}")
    save_as_json([round_values(value) for value in df["OBV"].tolist()], f"OBV_{frame}")


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

    save_as_json(
        [bool(value) for value in df["CDL_DOJI_10_0.1"].tolist()], "DOJI", PATH_PATTERN
    )
    save_as_json(
        [bool(value) for value in df["CDL_DOJISTAR"].tolist()], "DOJISTAR", PATH_PATTERN
    )
    save_as_json(
        [bool(value) for value in df["CDL_HAMMER"].tolist()], "HAMMER", PATH_PATTERN
    )
    save_as_json(
        [bool(value) for value in df["CDL_INVERTEDHAMMER"].tolist()],
        "INVERTEDHAMMER",
        PATH_PATTERN,
    )


def generate_heikin_candles():
    print("Generating heikin Candles")
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

    save_as_json(df.to_dict("records"), "test_candles_heikin_ashi", PATH_CANDLES)
    return df


def generate_heikin_candles_ema():
    print("Generating heikin EMA Candles")
    df = generate_heikin_candles()
    MyStrategy = ta.Strategy(name="Truth Source", ta=[{"kind": "ema"}])

    df.ta.strategy(MyStrategy)
    df = df.astype(object).replace(np.nan, None)
    save_as_json(
        [round_values(value) for value in df["EMA_10"].tolist()], "HEIKINASHI_EMA"
    )


def generate_z_candles():
    print("Generating Z Candles")
    df = pd.DataFrame.from_dict(load_json_candles())

    dfha = ta.cdl_z(df["open"], df["high"], df["low"], df["close"])
    df = pd.merge(df, dfha, right_index=True, left_index=True)
    df = df.astype(object).replace(np.nan, None)
    print_new(df)

    df.drop(columns=["open", "high", "low", "close"], axis=1, inplace=True)
    df.rename(
        columns={
            "open_Z_30_1": "open",
            "high_Z_30_1": "high",
            "low_Z_30_1": "low",
            "close_Z_30_1": "close",
        },
        inplace=True,
    )

    save_as_json(df.to_dict("records"), "test_candles_z", PATH_CANDLES)
    return df


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

    save_as_json(output, f"test_candles_{frame.replace('min', 'T')}", PATH_CANDLES)


if __name__ == "__main__":
    generate_indicators()
    generate_indicators_timeframe("5min")
    generate_indicators_timeframe("10min")
    generate_patterns()
    generate_timeframe_candles("5min")
    generate_timeframe_candles("10min")
    generate_heikin_candles()
    generate_heikin_candles_ema()
    generate_z_candles()
