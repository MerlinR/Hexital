import pytest
from hexital.candlesticks import HeikinAshi
from hexital.core.candle import Candle


@pytest.mark.usefixtures("candles", "candles_heikinashi")
def test_heikinashi(candles: list[Candle], candles_heikinashi: list[Candle]):
    heikin_ashi = HeikinAshi()
    heikin_ashi.set_candle_refs(candles)
    heikin_ashi.transform()

    assert heikin_ashi.derived_candles == candles_heikinashi
