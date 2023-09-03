import json

import pytest
from hexital import OHLCV


def load_json_candles() -> list:
    csv_file = open("tests/data/test_candles.json")
    return json.load(csv_file)


@pytest.fixture(name="candles")
def fixture_candle_data():
    return OHLCV.from_dicts(load_json_candles())