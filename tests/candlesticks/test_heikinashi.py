from typing import List

import pytest
from hexital.candlesticks.heikinashi import HeikinAshi
from hexital.core.candle import Candle


@pytest.mark.usefixtures("candles", "candles_heikinashi")
def test_heikinashi(candles: List[Candle], candles_heikinashi: List[Candle]):
    heikin_ashi = HeikinAshi()
    heikin_ashi.conversion(candles)

    assert candles == candles_heikinashi
