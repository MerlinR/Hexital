import json

import pytest

SOURCE_OF_TRUTH_PATH = "tests/data/source_of_truth/"


@pytest.fixture(name="expected_SMA")
def fixture_expected_sma():
    csv_files = open(f"{SOURCE_OF_TRUTH_PATH}/SMA.json")

    data = json.load(csv_files)
    return data


@pytest.fixture(name="expected_EMA")
def fixture_expected_ema():
    csv_files = open(f"{SOURCE_OF_TRUTH_PATH}/EMA.json")

    data = json.load(csv_files)
    return data


@pytest.fixture(name="expected_MACD")
def fixture_expected_macd():
    csv_files = open(f"{SOURCE_OF_TRUTH_PATH}/MACD.json")

    data = json.load(csv_files)
    return data


@pytest.fixture(name="expected_TR")
def fixture_expected_tr():
    csv_files = open(f"{SOURCE_OF_TRUTH_PATH}/TR.json")

    data = json.load(csv_files)
    return data


@pytest.fixture(name="expected_ATR")
def fixture_expected_atr():
    csv_files = open(f"{SOURCE_OF_TRUTH_PATH}/ATR.json")

    data = json.load(csv_files)
    return data
