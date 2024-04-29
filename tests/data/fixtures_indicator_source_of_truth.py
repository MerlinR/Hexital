import json

import pytest

SOURCE_OF_TRUTH_PATH = "tests/data/source_of_truth/indicators"
SOURCE_OF_TRUTH_HEX_PATH = "tests/data/source_of_truth/hex_indicators"


@pytest.fixture(name="expected_adx")
def fixture_expected_adx():
    csv_files = open(f"{SOURCE_OF_TRUTH_PATH}/ADX.json")
    return json.load(csv_files)


@pytest.fixture(name="expected_atr")
def fixture_expected_atr():
    csv_files = open(f"{SOURCE_OF_TRUTH_PATH}/ATR.json")
    return json.load(csv_files)


@pytest.fixture(name="expected_atr_20")
def fixture_expected_atr_20():
    csv_files = open(f"{SOURCE_OF_TRUTH_PATH}/ATR_20.json")
    return json.load(csv_files)


@pytest.fixture(name="expected_aroon")
def fixture_expected_aroon():
    csv_files = open(f"{SOURCE_OF_TRUTH_PATH}/AROON.json")
    return json.load(csv_files)


@pytest.fixture(name="expected_bbands")
def fixture_expected_bbands():
    csv_files = open(f"{SOURCE_OF_TRUTH_PATH}/BBANDS.json")
    return json.load(csv_files)


@pytest.fixture(name="expected_donchian")
def fixture_expected_donchian():
    csv_files = open(f"{SOURCE_OF_TRUTH_PATH}/DONCHIAN.json")
    return json.load(csv_files)


@pytest.fixture(name="expected_ema")
def fixture_expected_ema():
    csv_files = open(f"{SOURCE_OF_TRUTH_PATH}/EMA.json")
    return json.load(csv_files)


@pytest.fixture(name="expected_ema_t5")
def fixture_expected_ema_t5():
    csv_files = open(f"{SOURCE_OF_TRUTH_PATH}/EMA_5T.json")
    return json.load(csv_files)


@pytest.fixture(name="expected_ema_t10")
def fixture_expected_ema_t10():
    csv_files = open(f"{SOURCE_OF_TRUTH_PATH}/EMA_10T.json")
    return json.load(csv_files)


@pytest.fixture(name="expected_highlowaverage")
def fixture_expected_highlowaverage():
    csv_files = open(f"{SOURCE_OF_TRUTH_PATH}/HL2.json")
    return json.load(csv_files)


@pytest.fixture(name="expected_hma")
def fixture_expected_hma():
    csv_files = open(f"{SOURCE_OF_TRUTH_PATH}/HMA.json")
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


@pytest.fixture(name="expected_obv_t5")
def fixture_expected_OBV_t5():
    csv_files = open(f"{SOURCE_OF_TRUTH_PATH}/OBV_5T.json")
    return json.load(csv_files)


@pytest.fixture(name="expected_obv_t10")
def fixture_expected_OBV_t10():
    csv_files = open(f"{SOURCE_OF_TRUTH_PATH}/OBV_10T.json")
    return json.load(csv_files)


@pytest.fixture(name="expected_rma")
def fixture_expected_rma():
    csv_files = open(f"{SOURCE_OF_TRUTH_PATH}/RMA.json")
    return json.load(csv_files)


@pytest.fixture(name="expected_rma_20")
def fixture_expected_rma_20():
    csv_files = open(f"{SOURCE_OF_TRUTH_PATH}/RMA_20.json")
    return json.load(csv_files)


@pytest.fixture(name="expected_roc")
def fixture_expected_roc():
    csv_files = open(f"{SOURCE_OF_TRUTH_PATH}/ROC.json")
    return json.load(csv_files)


@pytest.fixture(name="expected_rsi")
def fixture_expected_rsi():
    csv_files = open(f"{SOURCE_OF_TRUTH_PATH}/RSI.json")
    return json.load(csv_files)


@pytest.fixture(name="expected_sma")
def fixture_expected_sma():
    csv_files = open(f"{SOURCE_OF_TRUTH_PATH}/SMA.json")
    return json.load(csv_files)


@pytest.fixture(name="expected_sma_3")
def fixture_expected_sma_3():
    csv_files = open(f"{SOURCE_OF_TRUTH_PATH}/SMA_3.json")
    return json.load(csv_files)


@pytest.fixture(name="expected_sma_t5")
def fixture_expected_sma_t5():
    csv_files = open(f"{SOURCE_OF_TRUTH_PATH}/SMA_5T.json")
    return json.load(csv_files)


@pytest.fixture(name="expected_sma_t10")
def fixture_expected_sma_t10():
    csv_files = open(f"{SOURCE_OF_TRUTH_PATH}/SMA_10T.json")
    return json.load(csv_files)


@pytest.fixture(name="expected_stdev")
def fixture_expected_stdev():
    csv_files = open(f"{SOURCE_OF_TRUTH_PATH}/STDEV.json")
    return json.load(csv_files)


@pytest.fixture(name="expected_stoch")
def fixture_expected_stoch():
    csv_files = open(f"{SOURCE_OF_TRUTH_PATH}/STOCH.json")
    return json.load(csv_files)


@pytest.fixture(name="expected_supertrend")
def fixture_expected_supertrend():
    csv_files = open(f"{SOURCE_OF_TRUTH_PATH}/SUPERTREND.json")
    return json.load(csv_files)


@pytest.fixture(name="expected_tr")
def fixture_expected_tr():
    csv_files = open(f"{SOURCE_OF_TRUTH_PATH}/TR.json")
    return json.load(csv_files)


@pytest.fixture(name="expected_tsi")
def fixture_expected_tsi():
    csv_files = open(f"{SOURCE_OF_TRUTH_PATH}/TSI.json")
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


# Hex Indicator


@pytest.fixture(name="expected_stdevthres")
def fixture_expected_stdevthres():
    csv_files = open(f"{SOURCE_OF_TRUTH_HEX_PATH}/STDEVTHRES.json")
    return json.load(csv_files)


@pytest.fixture(name="expected_counter_bear")
def fixture_expected_counter_bear():
    csv_files = open(f"{SOURCE_OF_TRUTH_HEX_PATH}/COUNTER_supertrend_bear.json")
    return json.load(csv_files)


@pytest.fixture(name="expected_counter_bull")
def fixture_expected_counter_bull():
    csv_files = open(f"{SOURCE_OF_TRUTH_HEX_PATH}/COUNTER_supertrend_bull.json")
    return json.load(csv_files)
