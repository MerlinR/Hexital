import json

import pytest

SOURCE_OF_TRUTH_PATH = "tests/data/source_of_truth/"


@pytest.fixture(name="expected_ATR")
def fixture_expected_atr():
    csv_files = open(f"{SOURCE_OF_TRUTH_PATH}/ATR.json")
    return json.load(csv_files)


@pytest.fixture(name="expected_EMA")
def fixture_expected_ema():
    csv_files = open(f"{SOURCE_OF_TRUTH_PATH}/EMA.json")
    return json.load(csv_files)


@pytest.fixture(name="expected_MACD")
def fixture_expected_macd():
    csv_files = open(f"{SOURCE_OF_TRUTH_PATH}/MACD.json")
    return json.load(csv_files)


@pytest.fixture(name="expected_RMA")
def fixture_expected_rma():
    csv_files = open(f"{SOURCE_OF_TRUTH_PATH}/RMA.json")
    return json.load(csv_files)


@pytest.fixture(name="expected_RSI")
def fixture_expected_rsi():
    csv_files = open(f"{SOURCE_OF_TRUTH_PATH}/RSI.json")
    return json.load(csv_files)


@pytest.fixture(name="expected_SMA")
def fixture_expected_sma():
    csv_files = open(f"{SOURCE_OF_TRUTH_PATH}/SMA.json")
    return json.load(csv_files)


@pytest.fixture(name="expected_WMA")
def fixture_expected_wma():
    csv_files = open(f"{SOURCE_OF_TRUTH_PATH}/WMA.json")
    return json.load(csv_files)


@pytest.fixture(name="expected_VWMA")
def fixture_expected_vwma():
    csv_files = open(f"{SOURCE_OF_TRUTH_PATH}/VWMA.json")
    return json.load(csv_files)


@pytest.fixture(name="expected_TR")
def fixture_expected_tr():
    csv_files = open(f"{SOURCE_OF_TRUTH_PATH}/TR.json")
    return json.load(csv_files)


@pytest.fixture(name="expected_SUPERTREND")
def fixture_expected_supertrend():
    csv_files = open(f"{SOURCE_OF_TRUTH_PATH}/SUPERTREND.json")
    return json.load(csv_files)
