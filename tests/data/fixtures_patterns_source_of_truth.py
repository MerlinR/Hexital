import json

import pytest

SOURCE_OF_TRUTH_PATH = "tests/data/source_of_truth/pattern"


@pytest.fixture(name="expected_doji")
def fixture_expected_doji():
    csv_files = open(f"{SOURCE_OF_TRUTH_PATH}/DOJI.json")
    return json.load(csv_files)
