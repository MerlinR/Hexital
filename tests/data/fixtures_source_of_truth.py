import json

import pytest

SOURCE_OF_TRUTH_PATH = "tests/data/source_of_truth/"


@pytest.fixture(name="expected_atr")
def fixture_expected_atr():
    csv_files = open(f"{SOURCE_OF_TRUTH_PATH}/ATR.json")
    return json.load(csv_files)


@pytest.fixture(name="expected_atr_20")
def fixture_expected_atr_20():
    csv_files = open(f"{SOURCE_OF_TRUTH_PATH}/ATR_20.json")
    return json.load(csv_files)


@pytest.fixture(name="expected_ema")
def fixture_expected_ema():
    csv_files = open(f"{SOURCE_OF_TRUTH_PATH}/EMA.json")
    return json.load(csv_files)


@pytest.fixture(name="expected_kc")
def fixture_expected_kc():
    csv_files = open(f"{SOURCE_OF_TRUTH_PATH}/KC.json")
    return json.load(csv_files)


@pytest.fixture(name="expected_macd")
def fixture_expected_macd():
    csv_files = open(f"{SOURCE_OF_TRUTH_PATH}/MACD.json")
    return json.load(csv_files)


@pytest.fixture(name="expected_obv")
def fixture_expected_OBV():
    csv_files = open(f"{SOURCE_OF_TRUTH_PATH}/OBV.json")
    return json.load(csv_files)


@pytest.fixture(name="expected_rma")
def fixture_expected_rma():
    csv_files = open(f"{SOURCE_OF_TRUTH_PATH}/RMA.json")
    return json.load(csv_files)


@pytest.fixture(name="expected_rsi")
def fixture_expected_rsi():
    csv_files = open(f"{SOURCE_OF_TRUTH_PATH}/RSI.json")
    return json.load(csv_files)


@pytest.fixture(name="expected_sma")
def fixture_expected_sma():
    csv_files = open(f"{SOURCE_OF_TRUTH_PATH}/SMA.json")
    return json.load(csv_files)


@pytest.fixture(name="expected_supertrend")
def fixture_expected_supertrend():
    csv_files = open(f"{SOURCE_OF_TRUTH_PATH}/SUPERTREND.json")
    return json.load(csv_files)


@pytest.fixture(name="expected_tr")
def fixture_expected_tr():
    csv_files = open(f"{SOURCE_OF_TRUTH_PATH}/TR.json")
    return json.load(csv_files)


@pytest.fixture(name="expected_vwap")
def fixture_expected_vwap():
    csv_files = open(f"{SOURCE_OF_TRUTH_PATH}/VWAP.json")
    return json.load(csv_files)


@pytest.fixture(name="expected_wma")
def fixture_expected_wma():
    csv_files = open(f"{SOURCE_OF_TRUTH_PATH}/WMA.json")
    return json.load(csv_files)


@pytest.fixture(name="expected_vwma")
def fixture_expected_vwma():
    csv_files = open(f"{SOURCE_OF_TRUTH_PATH}/VWMA.json")
    return json.load(csv_files)
