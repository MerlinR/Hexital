from collections.abc import Sequence
from typing import List

from hexital.core.candle import Candle
from hexital.core.candlestick_type import CandlestickType
from hexital.utils.weakreflist import WeakList


class HeikinAshi(CandlestickType):
    """Heikin-Ashi

    Heikin Ashi is a charting technique that can be used to predict future price movements.
    It is similar to traditional candlestick charts. However, unlike a regular candlestick
    chart, the Heikin Ashi chart tries to filter out some of the market noise by smoothing
    out strong price swings to better identify trend movements in the market.

    Sources:
        https://www.investopedia.com/trading/heikin-ashi-better-candlestick/
    """

    name: str = "Heikin-Ashi"
    acronym: str = "HA"
    candles: List[Candle]  # Fresh Candles
    derived_candles: WeakList[Candle]  # Transformed Candles

    def transform_candle(self, candle: Candle) -> None | Candle | Sequence[Candle]:
        candle_ = candle.clean_copy()
        prev_candle = self.prev_derived()
        candle_.close = (candle.open + candle.high + candle.low + candle.close) / 4

        if prev_candle := self.prev_derived():
            candle_.open = (prev_candle.open + prev_candle.close) / 2
        else:
            candle_.open = (candle.open + candle.close) / 2

        candle_.high = max(candle_.open, candle_.high, candle_.close)
        candle_.low = min(candle_.open, candle_.low, candle_.close)

        return candle_
