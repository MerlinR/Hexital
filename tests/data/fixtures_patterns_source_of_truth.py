import json

import pytest

SOURCE_OF_TRUTH_PATH = "tests/data/source_of_truth/pattern"


@pytest.fixture(name="expected_doji")
def fixture_expected_doji():
    csv_files = open(f"{SOURCE_OF_TRUTH_PATH}/DOJI.json")
    return json.load(csv_files)


@pytest.fixture(name="expected_dojistar")
def fixture_expected_dojistar():
    csv_files = open(f"{SOURCE_OF_TRUTH_PATH}/DOJISTAR.json")
    return json.load(csv_files)


@pytest.fixture(name="expected_hammer")
def fixture_expected_hammer():
    csv_files = open(f"{SOURCE_OF_TRUTH_PATH}/HAMMER.json")
    return json.load(csv_files)


@pytest.fixture(name="expected_inverted_hammer")
def fixture_expected_inverted_hammer():
    csv_files = open(f"{SOURCE_OF_TRUTH_PATH}/INVERTEDHAMMER.json")
    return json.load(csv_files)


@pytest.fixture(name="expected_bullish_engulfing")
def fixture_expected_bullish_engulfing():
    csv_files = open(f"{SOURCE_OF_TRUTH_PATH}/BULLISH_ENGULFING.json")
    return json.load(csv_files)


@pytest.fixture(name="expected_bearish_engulfing")
def fixture_expected_bearish_engulfing():
    csv_files = open(f"{SOURCE_OF_TRUTH_PATH}/BEARISH_ENGULFING.json")
    return json.load(csv_files)


@pytest.fixture(name="expected_bullish_harami")
def fixture_expected_bullish_harami():
    csv_files = open(f"{SOURCE_OF_TRUTH_PATH}/BULLISH_HARAMI.json")
    return json.load(csv_files)


@pytest.fixture(name="expected_bearish_harami")
def fixture_expected_bearish_harami():
    csv_files = open(f"{SOURCE_OF_TRUTH_PATH}/BEARISH_HARAMI.json")
    return json.load(csv_files)


@pytest.fixture(name="expected_hanging_man")
def fixture_expected_hanging_man():
    csv_files = open(f"{SOURCE_OF_TRUTH_PATH}/HANGINGMAN.json")
    return json.load(csv_files)


@pytest.fixture(name="expected_shooting_star")
def fixture_expected_shooting_star():
    csv_files = open(f"{SOURCE_OF_TRUTH_PATH}/SHOOTINGSTAR.json")
    return json.load(csv_files)


@pytest.fixture(name="expected_spinning_top")
def fixture_expected_spinning_top():
    csv_files = open(f"{SOURCE_OF_TRUTH_PATH}/SPINNINGTOP.json")
    return json.load(csv_files)
