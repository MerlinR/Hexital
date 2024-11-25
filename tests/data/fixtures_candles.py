import json
from datetime import datetime, timedelta

import pytest
from hexital import Candle

PATH = "tests/data/"
PATH_EXTRA = "tests/data/source_of_truth/candles/"


def load_json_candles(name: str, path: str) -> list:
    csv_file = open(f"{path}{name}.json")
    raw_candles = json.load(csv_file)
    for candle in raw_candles:
        candle["timestamp"] = datetime.strptime(candle["timestamp"], "%Y-%m-%dT%H:%M:%S")
    return raw_candles


@pytest.fixture(name="candles")
def fixture_candle_data():
    return Candle.from_dicts(load_json_candles("test_candles", PATH))


@pytest.fixture(name="candles_T5")
def fixture_candle_data_T5():
    candles = Candle.from_dicts(load_json_candles("test_candles_5T", PATH_EXTRA))
    for candle in candles:
        candle.timeframe = timedelta(minutes=5)
        candle.aggregation_factor = 5

    candles[-1].aggregation_factor = 2
    candles[9].aggregation_factor = 4
    candles[22].aggregation_factor = 4
    return candles


@pytest.fixture(name="candles_T10")
def fixture_candle_data_T10():
    candles = Candle.from_dicts(load_json_candles("test_candles_10T", PATH_EXTRA))
    for candle in candles:
        candle.timeframe = timedelta(minutes=10)
        candle.aggregation_factor = 10

    candles[-1].aggregation_factor = 2
    candles[4].aggregation_factor = 9
    candles[11].aggregation_factor = 9
    return candles


@pytest.fixture(name="candles_heikinashi")
def fixture_candle_data_heikinashi():
    return Candle.from_dicts(load_json_candles("test_candles_heikin_ashi", PATH_EXTRA))


@pytest.fixture(name="minimal_candles")
def fixture_minimal_candles():
    candles = [
        Candle(
            open=17213,
            high=2395,
            low=7813,
            close=3615,
            volume=19661,
            indicators={"ATR": 100, "NATR": {"nested": 101}, "NoneATR": {"nested": None}},
            sub_indicators={"SATR": 110, "SSATR": {"nested": 111}},
            timestamp=datetime(2023, 6, 1, 9, 0, 10),
        ),
        Candle(
            open=1301,
            high=3007,
            low=11626,
            close=19048,
            volume=28909,
            indicators={"ATR": 200, "NATR": {"nested": 201}, "NoneATR": {"nested": 1}},
            sub_indicators={"SATR": 210, "SSATR": {"nested": 211}},
            timestamp=datetime(2023, 6, 1, 9, 1, 0),
        ),
        Candle(
            open=12615,
            high=923,
            low=7318,
            close=1351,
            volume=33765,
            indicators={"ATR": 300, "NATR": {"nested": 301}, "NoneATR": {"nested": 2}},
            sub_indicators={"SATR": 310, "SSATR": {"nested": 311}},
            timestamp=datetime(2023, 6, 1, 9, 2, 0),
        ),
        Candle(
            open=1643,
            high=16229,
            low=17721,
            close=212,
            volume=3281,
            indicators={"ATR": 400, "NATR": {"nested": 401}, "NoneATR": {"nested": 3}},
            sub_indicators={"SATR": 410, "SSATR": {"nested": 411}},
            timestamp=datetime(2023, 6, 1, 9, 3, 0),
        ),
        Candle(
            open=424,
            high=10614,
            low=17133,
            close=7308,
            volume=41793,
            indicators={"ATR": 500, "NATR": {"nested": 501}, "NoneATR": {"nested": 4}},
            sub_indicators={"SATR": 510, "SSATR": {"nested": 511}},
            timestamp=datetime(2023, 6, 1, 9, 4, 0),
        ),
        Candle(
            open=4323,
            high=5858,
            low=8785,
            close=8418,
            volume=34913,
            indicators={"ATR": 600, "NATR": {"nested": 601}, "NoneATR": {"nested": 5}},
            sub_indicators={"SATR": 610, "SSATR": {"nested": 611}},
            timestamp=datetime(2023, 6, 1, 9, 5, 0),
        ),
        Candle(
            open=13838,
            high=13533,
            low=4830,
            close=17765,
            volume=586,
            indicators={"ATR": 700, "NATR": {"nested": 701}},
            sub_indicators={"SATR": 710, "SSATR": {"nested": 711}},
            timestamp=datetime(2023, 6, 1, 9, 6, 0),
        ),
        Candle(
            open=14373,
            high=18026,
            low=7844,
            close=18798,
            volume=25993,
            indicators={"ATR": 800, "NATR": {"nested": 801}},
            sub_indicators={"SATR": 810, "SSATR": {"nested": 811}},
            timestamp=datetime(2023, 6, 1, 9, 7, 0),
        ),
        Candle(
            open=12382,
            high=19875,
            low=2853,
            close=1431,
            volume=10055,
            indicators={"ATR": 900, "NATR": {"nested": 901}},
            sub_indicators={"SATR": 910, "SSATR": {"nested": 911}},
            timestamp=datetime(2023, 6, 1, 9, 8, 0),
        ),
        Candle(
            open=19202,
            high=6584,
            low=6349,
            close=8299,
            volume=13199,
            indicators={"ATR": 1000, "NATR": {"nested": 1001}},
            sub_indicators={"SATR": 1010, "SSATR": {"nested": 1011}},
            timestamp=datetime(2023, 6, 1, 9, 9, 0),
        ),
        Candle(
            open=19723,
            high=4837,
            low=11631,
            close=6231,
            volume=38993,
            indicators={"ATR": 1100, "NATR": {"nested": 1101}, "MinTR": 1102},
            sub_indicators={"SATR": 1110, "SSATR": {"nested": 1111}},
            timestamp=datetime(2023, 6, 1, 9, 10, 0),
        ),
        Candle(
            open=13564,
            high=12390,
            low=590,
            close=13416,
            volume=30262,
            indicators={"ATR": 1200, "NATR": {"nested": 1201}, "MinTR": 1202},
            sub_indicators={"SATR": 1210, "SSATR": {"nested": 1211}},
            timestamp=datetime(2023, 6, 1, 9, 11, 0),
        ),
        Candle(
            open=16319,
            high=5892,
            low=16665,
            close=5776,
            volume=47713,
            indicators={"ATR": 1300, "NATR": {"nested": 1301}, "MinTR": 1302},
            sub_indicators={"SATR": 1310, "SSATR": {"nested": 1311}},
            timestamp=datetime(2023, 6, 1, 9, 12, 0),
        ),
        Candle(
            open=4709,
            high=8190,
            low=10053,
            close=5062,
            volume=14711,
            indicators={"ATR": 1400, "NATR": {"nested": 1401}, "MinTR": 1402},
            sub_indicators={"SATR": 1410, "SSATR": {"nested": 1411}},
            timestamp=datetime(2023, 6, 1, 9, 13, 0),
        ),
        Candle(
            open=15803,
            high=5167,
            low=17880,
            close=8916,
            volume=36686,
            indicators={"ATR": 1500, "NATR": {"nested": 1501}, "MinTR": 1502},
            sub_indicators={"SATR": 1510, "SSATR": {"nested": 1511}},
            timestamp=datetime(2023, 6, 1, 9, 14, 0),
        ),
        Candle(
            open=16425,
            high=1398,
            low=18365,
            close=19637,
            volume=41744,
            indicators={"ATR": 1600, "NATR": {"nested": 1601}, "MinTR": 1602},
            sub_indicators={"SATR": 1610, "SSATR": {"nested": 1611}},
            timestamp=datetime(2023, 6, 1, 9, 15, 0),
        ),
        Candle(
            open=19535,
            high=3624,
            low=12972,
            close=12862,
            volume=47128,
            indicators={"ATR": 1700, "NATR": {"nested": 1701}, "MinTR": 1702},
            sub_indicators={"SATR": 1710, "SSATR": {"nested": 1711}},
            timestamp=datetime(2023, 6, 1, 9, 16, 0),
        ),
        Candle(
            open=5837,
            high=11555,
            low=16429,
            close=18501,
            volume=9,
            indicators={"ATR": 1800, "NATR": {"nested": 1801}, "MinTR": 1802},
            sub_indicators={"SATR": 1810, "SSATR": {"nested": 1811}},
            timestamp=datetime(2023, 6, 1, 9, 17, 0),
        ),
        Candle(
            open=16346,
            high=4309,
            low=1903,
            close=6255,
            volume=31307,
            indicators={"ATR": 1900, "NATR": {"nested": 1901}, "MinTR": 1902},
            sub_indicators={"SATR": 1910, "SSATR": {"nested": 1911}},
            timestamp=datetime(2023, 6, 1, 9, 18, 0),
        ),
        Candle(
            open=2424,
            high=10767,
            low=13115,
            close=13649,
            volume=15750,
            indicators={"ATR": 2000, "NATR": {"nested": 2001}, "MinTR": 2002},
            sub_indicators={"SATR": 2010, "SSATR": {"nested": 2011}},
            timestamp=datetime(2023, 6, 1, 9, 19, 0),
        ),
    ]

    return candles


@pytest.fixture(name="minimal_candles_t5")
def fixture_minimal_candles_5_minute():
    candles = [
        Candle(
            open=17213,
            high=16229,
            low=7318,
            close=8418,
            volume=162322,
            indicators={},
            sub_indicators={},
            timestamp=datetime(2023, 6, 1, 9, 5, 0),
        ),
        Candle(
            open=13838,
            high=19875,
            low=2853,
            close=6231,
            volume=88826,
            indicators={},
            sub_indicators={},
            timestamp=datetime(2023, 6, 1, 9, 10, 0),
        ),
        Candle(
            open=13564,
            high=12390,
            low=590,
            close=19637,
            volume=171116,
            indicators={},
            sub_indicators={},
            timestamp=datetime(2023, 6, 1, 9, 15, 0),
        ),
        Candle(
            open=19535,
            high=11555,
            low=1903,
            close=13649,
            volume=94194,
            indicators={},
            sub_indicators={},
            timestamp=datetime(2023, 6, 1, 9, 20, 0),
        ),
    ]
    candles[0].aggregation_factor = 6
    candles[1].aggregation_factor = 5
    candles[2].aggregation_factor = 5
    candles[3].aggregation_factor = 4
    return candles


@pytest.fixture(name="minimal_candles_t10")
def fixture_minimal_candles_10_minute():
    candles = [
        Candle(
            open=17213,
            high=19875,
            low=2853,
            close=6231,
            volume=251148,
            indicators={},
            sub_indicators={},
            timestamp=datetime(2023, 6, 1, 9, 10, 0),
        ),
        Candle(
            open=13564,
            high=12390,
            low=590,
            close=13649,
            volume=265310,
            indicators={},
            sub_indicators={},
            timestamp=datetime(2023, 6, 1, 9, 20, 0),
        ),
    ]
    candles[0].aggregation_factor = 11
    candles[1].aggregation_factor = 9
    return candles
