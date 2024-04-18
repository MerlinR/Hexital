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
