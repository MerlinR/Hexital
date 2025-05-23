from random import randrange

import pytest
from hexital import exceptions, indicators
from hexital.utils.common import CalcMode

from .indicator_testbase import IndicatorTestBase


class TestIndicators(IndicatorTestBase):
    @pytest.mark.usefixtures("candles", "expected_adx")
    def test_adx(self, candles, expected_adx):
        test = indicators.ADX(candles=candles)
        test.calculate()
        assert self.verify(test.readings(), expected_adx, amount=390)

    @pytest.mark.usefixtures("candles", "expected_atr")
    def test_atr(self, candles, expected_atr):
        test = indicators.ATR(candles=candles)
        test.calculate()
        assert self.verify(test.readings(), expected_atr)

    @pytest.mark.usefixtures("candles", "expected_atr_20")
    def test_atr_20(self, candles, expected_atr_20):
        test = indicators.ATR(candles=candles, period=20)
        test.calculate()
        assert self.verify(test.readings(), expected_atr_20)

    @pytest.mark.usefixtures("candles", "expected_aroon")
    def test_aroon(self, candles, expected_aroon):
        test = indicators.AROON(candles=candles)
        test.calculate()
        assert self.verify(test.readings(), expected_aroon)

    @pytest.mark.usefixtures("candles", "expected_bbands")
    def test_bbands(self, candles, expected_bbands):
        test = indicators.BBANDS(candles=candles)
        test.calculate()
        assert self.verify(test.readings(), expected_bbands)

    @pytest.mark.usefixtures("candles", "expected_cmo")
    def test_cmo(self, candles, expected_cmo):
        test = indicators.CMO(candles=candles)
        test.calculate()
        assert self.verify(test.readings(), expected_cmo)

    @pytest.mark.usefixtures("candles", "expected_donchian")
    def test_donchian(self, candles, expected_donchian):
        test = indicators.Donchian(candles=candles)
        test.calculate()
        assert self.verify(test.readings(), expected_donchian)

    @pytest.mark.usefixtures("candles", "expected_ema")
    def test_ema(self, candles, expected_ema):
        test = indicators.EMA(candles=candles)
        test.calculate()
        assert self.verify(test.readings(), expected_ema)

    @pytest.mark.usefixtures("candles", "expected_ema")
    def test_ema_append(self, candles, expected_ema):
        test = indicators.EMA(candles=[])
        for candle in candles:
            test.append(candle)
        assert self.verify(test.readings(), expected_ema)

    @pytest.mark.usefixtures("candles", "expected_ema")
    def test_ema_prepend(self, candles, expected_ema):
        test = indicators.EMA(candles=[])
        for candle in reversed(candles):
            test.prepend(candle)
        assert self.verify(test.readings(), expected_ema)

    @pytest.mark.usefixtures("candles", "expected_ema")
    def test_ema_insert(self, candles, expected_ema):
        test = indicators.EMA(candles=[])
        while candles:
            test.insert(candles.pop(randrange(len(candles))))

        assert self.verify(test.readings(), expected_ema)

    @pytest.mark.usefixtures("candles", "expected_ema_t5")
    def test_ema_t5(self, candles, expected_ema_t5):
        test = indicators.EMA(candles=candles, timeframe="t5")
        test.calculate()
        assert self.verify(test.readings(), expected_ema_t5)

    @pytest.mark.usefixtures("candles", "expected_ema_t10")
    def test_ema_t10(self, candles, expected_ema_t10):
        test = indicators.EMA(candles=candles, timeframe="t10")
        test.calculate()
        assert self.verify(test.readings(), expected_ema_t10)

    @pytest.mark.usefixtures("candles", "expected_highlowaverage")
    def test_highlowaverage(self, candles, expected_highlowaverage):
        test = indicators.HLA(candles=candles)
        test.calculate()
        assert self.verify(test.readings(), expected_highlowaverage)

    @pytest.mark.usefixtures("candles", "expected_highlowcloseaverage")
    def test_highlowcloseaverage(self, candles, expected_highlowcloseaverage):
        test = indicators.HLCA(candles=candles)
        test.calculate()
        assert self.verify(test.readings(), expected_highlowcloseaverage)

    @pytest.mark.usefixtures("candles", "expected_hma")
    def test_hma(self, candles, expected_hma):
        test = indicators.HMA(candles=candles)
        test.calculate()
        assert self.verify(test.readings(), expected_hma)

    @pytest.mark.usefixtures("candles", "expected_jma")
    def test_jma(self, candles, expected_jma):
        test = indicators.JMA(candles=candles)
        test.calculate()
        assert self.verify(test.readings(), expected_jma, acceptable_diff=6)

    @pytest.mark.usefixtures("candles", "expected_jma_extra")
    def test_jma_extra(self, candles, expected_jma_extra):
        test = indicators.JMA(candles=candles, period=10, phase=80.0)
        test.calculate()
        assert self.verify(test.readings(), expected_jma_extra, acceptable_diff=9)

    @pytest.mark.usefixtures("candles", "expected_kc")
    def test_kc(self, candles, expected_kc):
        test = indicators.KC(candles=candles)
        test.calculate()
        assert self.verify(test.readings(), expected_kc)

    @pytest.mark.usefixtures("candles", "expected_macd")
    def test_macd(self, candles, expected_macd):
        test = indicators.MACD(candles=candles)
        test.calculate()
        assert self.verify(test.readings(), expected_macd, amount=400)

    @pytest.mark.usefixtures("candles", "expected_mfi")
    def test_mfi(self, candles, expected_mfi):
        test = indicators.MFI(candles=candles)
        test.calculate()
        assert self.verify(test.readings(), expected_mfi)

    @pytest.mark.usefixtures("candles", "expected_midpoint")
    def test_mop(self, candles, expected_midpoint):
        test = indicators.MOP(candles=candles)
        test.calculate()
        assert self.verify(test.readings(), expected_midpoint)

    @pytest.mark.usefixtures("candles", "expected_obv")
    def test_obv(self, candles, expected_obv):
        test = indicators.OBV(candles=candles)
        test.calculate()
        assert self.verify(test.readings(), expected_obv)

    @pytest.mark.usefixtures("candles", "expected_obv_t5")
    def test_obv_t5(self, candles, expected_obv_t5):
        test = indicators.OBV(candles=candles, timeframe="t5")
        test.calculate()
        assert self.verify(test.readings(), expected_obv_t5)

    @pytest.mark.usefixtures("candles", "expected_obv_t10")
    def test_obv_t10(self, candles, expected_obv_t10):
        test = indicators.OBV(candles=candles, timeframe="t10")
        test.calculate()
        assert self.verify(test.readings(), expected_obv_t10)

    @pytest.mark.usefixtures("candles", "expected_obv_t10")
    def test_obv_t10_double_resample(self, candles, expected_obv_t10):
        test = indicators.OBV(candles=candles, timeframe="t10")
        test._candle_mngr.resample_candles(CalcMode.INSERT)
        test.calculate()

        assert self.verify(test.readings(), expected_obv_t10, verbose=True)

    @pytest.mark.usefixtures("candles", "expected_rma")
    def test_rma(self, candles, expected_rma):
        test = indicators.RMA(candles=candles)
        test.calculate()
        assert self.verify(test.readings(), expected_rma)

    @pytest.mark.usefixtures("candles", "expected_rma_20")
    def test_rma_20(self, candles, expected_rma_20):
        test = indicators.RMA(candles=candles, period=20)
        test.calculate()
        assert self.verify(test.readings(), expected_rma_20)

    @pytest.mark.usefixtures("candles", "expected_roc")
    def test_roc(self, candles, expected_roc):
        test = indicators.ROC(candles=candles)
        test.calculate()
        assert self.verify(test.readings(), expected_roc)

    @pytest.mark.usefixtures("candles", "expected_rsi")
    def test_rsi(self, candles, expected_rsi):
        test = indicators.RSI(candles=candles)
        test.calculate()
        assert self.verify(test.readings(), expected_rsi)

    @pytest.mark.usefixtures("candles", "expected_rvi")
    def test_rvi(self, candles, expected_rvi):
        test = indicators.RVI(candles=candles)
        test.calculate()
        assert self.verify(test.readings(), expected_rvi)

    @pytest.mark.usefixtures("candles", "expected_rsi")
    def test_append_rsi(self, candles, expected_rsi):
        test = indicators.RSI(candles=[])
        for candle in candles:
            test.append(candle)

        assert self.verify(test.readings(), expected_rsi)

    @pytest.mark.usefixtures("candles", "expected_sma")
    def test_sma(self, candles, expected_sma):
        test = indicators.SMA(candles=candles)
        test.calculate()
        assert self.verify(test.readings(), expected_sma)

    @pytest.mark.usefixtures("candles", "expected_sma_3")
    def test_sma_3(self, candles, expected_sma_3):
        test = indicators.SMA(candles=candles, period=3)
        test.calculate()
        assert self.verify(test.readings(), expected_sma_3)

    @pytest.mark.usefixtures("candles", "expected_sma_t5")
    def test_sma_t5(self, candles, expected_sma_t5):
        test = indicators.SMA(candles=candles, timeframe="t5")
        test.calculate()
        assert self.verify(test.readings(), expected_sma_t5)

    @pytest.mark.usefixtures("candles", "expected_sma_t10")
    def test_sma_t10(self, candles, expected_sma_t10):
        test = indicators.SMA(candles=candles, timeframe="t10")
        test.calculate()
        assert self.verify(test.readings(), expected_sma_t10)

    @pytest.mark.usefixtures("candles", "expected_stdev")
    def test_stdev(self, candles, expected_stdev):
        test = indicators.STDEV(candles=candles)
        test.calculate()
        assert self.verify(test.readings(), expected_stdev)

    @pytest.mark.usefixtures("candles", "expected_stoch")
    def test_stoch(self, candles, expected_stoch):
        test = indicators.STOCH(candles=candles)
        test.calculate()
        assert self.verify(test.readings(), expected_stoch)

    @pytest.mark.usefixtures("candles", "expected_supertrend")
    def test_supertrend(self, candles, expected_supertrend):
        test = indicators.Supertrend(candles=candles)
        test.calculate()

        assert self.verify(test.readings(), expected_supertrend)

    @pytest.mark.usefixtures("candles", "expected_supertrend")
    def test_append_supertrend(self, candles, expected_supertrend):
        test = indicators.Supertrend(candles=[])
        for candle in candles:
            test.append(candle)
        assert self.verify(test.readings(), expected_supertrend)

    @pytest.mark.usefixtures("candles", "expected_tr")
    def test_tr(self, candles, expected_tr):
        test = indicators.TR(candles=candles)
        test.calculate()
        assert self.verify(test.readings(), expected_tr)

    @pytest.mark.usefixtures("candles", "expected_tsi")
    def test_tsi(self, candles, expected_tsi):
        test = indicators.TSI(candles=candles)
        test.calculate()
        assert self.verify(test.readings(), expected_tsi)

    @pytest.mark.usefixtures("candles", "expected_vwap")
    def test_vwap(self, candles, expected_vwap):
        test = indicators.VWAP(candles=candles)
        test.calculate()
        assert self.verify(test.readings(), expected_vwap)

    @pytest.mark.usefixtures("candles", "expected_vwap")
    def test_vwap_append(self, candles, expected_vwap):
        test = indicators.VWAP(candles=[])
        for candle in candles:
            test.append(candle)

        assert self.verify(test.readings(), expected_vwap)

    @pytest.mark.usefixtures("candles", "expected_vwap_h1")
    def test_vwap_anchor(self, candles, expected_vwap_h1):
        test = indicators.VWAP(candles=candles, anchor="H1")
        test.calculate()
        assert self.verify(test.readings(), expected_vwap_h1)

    @pytest.mark.usefixtures("candles", "expected_vwap_h1")
    def test_vwap_anchor_invalid(self, candles, expected_vwap_h1):
        with pytest.raises(exceptions.InvalidConfiguration):
            test = indicators.VWAP(candles=candles, anchor="1")

    @pytest.mark.usefixtures("candles", "expected_vwma")
    def test_vwma(self, candles, expected_vwma):
        test = indicators.VWMA(candles=candles)
        test.calculate()
        assert self.verify(test.readings(), expected_vwma)

    @pytest.mark.usefixtures("candles", "expected_wma")
    def test_wma(self, candles, expected_wma):
        test = indicators.WMA(candles=candles)
        test.calculate()
        assert self.verify(test.readings(), expected_wma)
