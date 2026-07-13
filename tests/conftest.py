CANDLE_DATA = [
    "tests.data.fixtures_candles",
    "tests.data.fixtures_candles_conversion",
    "tests.data.fixtures_indicator_source_of_truth",
    "tests.data.fixtures_patterns_source_of_truth",
]

import pytest

from hexital.core.indicator_registry import clear_registry


@pytest.fixture(autouse=True)
def _reset_indicator_registry():
    clear_registry()
    yield
    clear_registry()


pytest_plugins = [*CANDLE_DATA]
