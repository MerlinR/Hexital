import pytest
from hexital.candlesticks import HeikinAshi, Renko
from hexital.core.candle import Candle


@pytest.mark.usefixtures("candles", "candles_heikinashi")
def test_heikinashi(candles: list[Candle], candles_heikinashi: list[Candle]):
    heikin_ashi = HeikinAshi()
    heikin_ashi.set_candle_refs(candles)
    heikin_ashi.transform()

    assert heikin_ashi.derived_candles == candles_heikinashi


@pytest.mark.usefixtures("candles", "candles_renko")
def test_renko(candles: list[Candle], candles_renko: list[Candle]):
    renko = Renko()
    renko.set_candle_refs(candles)
    renko.transform()

    assert renko.derived_candles == candles_renko
