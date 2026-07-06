import json

import pytest

SOURCE_OF_TRUTH_PATH = "tests/data/source_of_truth/indicators"
SOURCE_OF_TRUTH_HEX_PATH = "tests/data/source_of_truth/hex_indicators"


def load_fixture(path: str) -> list | dict:
    with open(path) as fixture_file:
        return json.load(fixture_file)


@pytest.fixture(name="expected_adx")
def fixture_expected_adx():
    return load_fixture(f"{SOURCE_OF_TRUTH_PATH}/ADX.json")


@pytest.fixture(name="expected_atr")
def fixture_expected_atr():
    return load_fixture(f"{SOURCE_OF_TRUTH_PATH}/ATR.json")


@pytest.fixture(name="expected_atr_20")
def fixture_expected_atr_20():
    return load_fixture(f"{SOURCE_OF_TRUTH_PATH}/ATR_20.json")


@pytest.fixture(name="expected_aroon")
def fixture_expected_aroon():
    return load_fixture(f"{SOURCE_OF_TRUTH_PATH}/AROON.json")


@pytest.fixture(name="expected_bbands")
def fixture_expected_bbands():
    return load_fixture(f"{SOURCE_OF_TRUTH_PATH}/BBANDS.json")


@pytest.fixture(name="expected_cci")
def fixture_expected_cci():
    return load_fixture(f"{SOURCE_OF_TRUTH_PATH}/CCI.json")


@pytest.fixture(name="expected_cmo")
def fixture_expected_cmo():
    return load_fixture(f"{SOURCE_OF_TRUTH_PATH}/CMO.json")


@pytest.fixture(name="expected_dema")
def fixture_expected_dema():
    return load_fixture(f"{SOURCE_OF_TRUTH_PATH}/DEMA.json")


@pytest.fixture(name="expected_donchian")
def fixture_expected_donchian():
    return load_fixture(f"{SOURCE_OF_TRUTH_PATH}/DONCHIAN.json")


@pytest.fixture(name="expected_ema")
def fixture_expected_ema():
    return load_fixture(f"{SOURCE_OF_TRUTH_PATH}/EMA.json")


@pytest.fixture(name="expected_ema_t5")
def fixture_expected_ema_t5():
    return load_fixture(f"{SOURCE_OF_TRUTH_PATH}/EMA_5T.json")


@pytest.fixture(name="expected_ema_t10")
def fixture_expected_ema_t10():
    return load_fixture(f"{SOURCE_OF_TRUTH_PATH}/EMA_10T.json")


@pytest.fixture(name="expected_highlowaverage")
def fixture_expected_highlowaverage():
    return load_fixture(f"{SOURCE_OF_TRUTH_PATH}/HL2.json")


@pytest.fixture(name="expected_highlowcloseaverage")
def fixture_expected_highlowcloseaverage():
    return load_fixture(f"{SOURCE_OF_TRUTH_PATH}/HLC.json")


@pytest.fixture(name="expected_hma")
def fixture_expected_hma():
    return load_fixture(f"{SOURCE_OF_TRUTH_PATH}/HMA.json")


@pytest.fixture(name="expected_ichimoku")
def fixture_expected_ichimoku():
    return load_fixture(f"{SOURCE_OF_TRUTH_PATH}/ICHIMOKU.json")


@pytest.fixture(name="expected_jma")
def fixture_expected_jma():
    return load_fixture(f"{SOURCE_OF_TRUTH_PATH}/JMA.json")


@pytest.fixture(name="expected_jma_extra")
def fixture_expected_jma_extra():
    return load_fixture(f"{SOURCE_OF_TRUTH_PATH}/JMA_extra.json")


@pytest.fixture(name="expected_kama")
def fixture_expected_kama():
    return load_fixture(f"{SOURCE_OF_TRUTH_PATH}/KAMA.json")


@pytest.fixture(name="expected_kc")
def fixture_expected_kc():
    return load_fixture(f"{SOURCE_OF_TRUTH_PATH}/KC.json")


@pytest.fixture(name="expected_macd")
def fixture_expected_macd():
    return load_fixture(f"{SOURCE_OF_TRUTH_PATH}/MACD.json")


@pytest.fixture(name="expected_mfi")
def fixture_expected_mfi():
    return load_fixture(f"{SOURCE_OF_TRUTH_PATH}/MFI.json")


@pytest.fixture(name="expected_midpoint")
def fixture_expected_midpoint():
    return load_fixture(f"{SOURCE_OF_TRUTH_PATH}/MIDPOINT.json")


@pytest.fixture(name="expected_natr")
def fixture_expected_natr():
    return load_fixture(f"{SOURCE_OF_TRUTH_PATH}/NATR.json")


@pytest.fixture(name="expected_obv")
def fixture_expected_OBV():
    return load_fixture(f"{SOURCE_OF_TRUTH_PATH}/OBV.json")


@pytest.fixture(name="expected_obv_t5")
def fixture_expected_OBV_t5():
    return load_fixture(f"{SOURCE_OF_TRUTH_PATH}/OBV_5T.json")


@pytest.fixture(name="expected_obv_t10")
def fixture_expected_OBV_t10():
    return load_fixture(f"{SOURCE_OF_TRUTH_PATH}/OBV_10T.json")


@pytest.fixture(name="expected_ppo")
def fixture_expected_ppo():
    return load_fixture(f"{SOURCE_OF_TRUTH_PATH}/PPO.json")


@pytest.fixture(name="expected_psar")
def fixture_expected_psar():
    return load_fixture(f"{SOURCE_OF_TRUTH_PATH}/PSAR.json")


@pytest.fixture(name="expected_rma")
def fixture_expected_rma():
    return load_fixture(f"{SOURCE_OF_TRUTH_PATH}/RMA.json")


@pytest.fixture(name="expected_rma_20")
def fixture_expected_rma_20():
    return load_fixture(f"{SOURCE_OF_TRUTH_PATH}/RMA_20.json")


@pytest.fixture(name="expected_roc")
def fixture_expected_roc():
    return load_fixture(f"{SOURCE_OF_TRUTH_PATH}/ROC.json")


@pytest.fixture(name="expected_rsi")
def fixture_expected_rsi():
    return load_fixture(f"{SOURCE_OF_TRUTH_PATH}/RSI.json")


@pytest.fixture(name="expected_rvi")
def fixture_expected_rvi():
    return load_fixture(f"{SOURCE_OF_TRUTH_PATH}/RVI.json")


@pytest.fixture(name="expected_sma")
def fixture_expected_sma():
    return load_fixture(f"{SOURCE_OF_TRUTH_PATH}/SMA.json")


@pytest.fixture(name="expected_sma_3")
def fixture_expected_sma_3():
    return load_fixture(f"{SOURCE_OF_TRUTH_PATH}/SMA_3.json")


@pytest.fixture(name="expected_sma_t5")
def fixture_expected_sma_t5():
    return load_fixture(f"{SOURCE_OF_TRUTH_PATH}/SMA_5T.json")


@pytest.fixture(name="expected_sma_t10")
def fixture_expected_sma_t10():
    return load_fixture(f"{SOURCE_OF_TRUTH_PATH}/SMA_10T.json")


@pytest.fixture(name="expected_squeeze")
def fixture_expected_squeeze():
    return load_fixture(f"{SOURCE_OF_TRUTH_PATH}/SQUEEZE.json")


@pytest.fixture(name="expected_squeeze_pro")
def fixture_expected_squeeze_pro():
    return load_fixture(f"{SOURCE_OF_TRUTH_PATH}/SQUEEZE_PRO.json")


@pytest.fixture(name="expected_stdev")
def fixture_expected_stdev():
    return load_fixture(f"{SOURCE_OF_TRUTH_PATH}/STDEV.json")


@pytest.fixture(name="expected_stoch")
def fixture_expected_stoch():
    return load_fixture(f"{SOURCE_OF_TRUTH_PATH}/STOCH.json")


@pytest.fixture(name="expected_supertrend")
def fixture_expected_supertrend():
    return load_fixture(f"{SOURCE_OF_TRUTH_PATH}/SUPERTREND.json")


@pytest.fixture(name="expected_tr")
def fixture_expected_tr():
    return load_fixture(f"{SOURCE_OF_TRUTH_PATH}/TR.json")


@pytest.fixture(name="expected_tsi")
def fixture_expected_tsi():
    return load_fixture(f"{SOURCE_OF_TRUTH_PATH}/TSI.json")


@pytest.fixture(name="expected_uo")
def fixture_expected_uo():
    return load_fixture(f"{SOURCE_OF_TRUTH_PATH}/UO.json")


@pytest.fixture(name="expected_willr")
def fixture_expected_willr():
    return load_fixture(f"{SOURCE_OF_TRUTH_PATH}/WILLR.json")


@pytest.fixture(name="expected_vwap")
def fixture_expected_vwap():
    return load_fixture(f"{SOURCE_OF_TRUTH_PATH}/VWAP.json")


@pytest.fixture(name="expected_vwap_h1")
def fixture_expected_vwap_h():
    return load_fixture(f"{SOURCE_OF_TRUTH_PATH}/VWAP_H1.json")


@pytest.fixture(name="expected_wma")
def fixture_expected_wma():
    return load_fixture(f"{SOURCE_OF_TRUTH_PATH}/WMA.json")


@pytest.fixture(name="expected_vwma")
def fixture_expected_vwma():
    return load_fixture(f"{SOURCE_OF_TRUTH_PATH}/VWMA.json")


@pytest.fixture(name="expected_zscore")
def fixture_expected_zscore():
    return load_fixture(f"{SOURCE_OF_TRUTH_PATH}/ZSCORE.json")


# Hex Indicator


@pytest.fixture(name="expected_stdevt")
def fixture_expected_stdevt():
    return load_fixture(f"{SOURCE_OF_TRUTH_HEX_PATH}/STDEVT.json")


@pytest.fixture(name="expected_highestlowest")
def fixture_expected_highestlowest():
    return load_fixture(f"{SOURCE_OF_TRUTH_HEX_PATH}/HIGHESTLOWEST.json")


@pytest.fixture(name="expected_counter_bear")
def fixture_expected_counter_bear():
    return load_fixture(f"{SOURCE_OF_TRUTH_HEX_PATH}/COUNTER_supertrend_bear.json")


@pytest.fixture(name="expected_counter_bull")
def fixture_expected_counter_bull():
    return load_fixture(f"{SOURCE_OF_TRUTH_HEX_PATH}/COUNTER_supertrend_bull.json")


@pytest.fixture(name="expected_pivotpoints")
def fixture_expected_pivotpoints():
    return load_fixture(f"{SOURCE_OF_TRUTH_HEX_PATH}/PIVOTPOINTS.json")


# Candlesticks


@pytest.fixture(name="expected_heikinashi_ema")
def fixture_candle_data_heikinashi_ema():
    return load_fixture(f"{SOURCE_OF_TRUTH_PATH}/HEIKINASHI_EMA.json")
