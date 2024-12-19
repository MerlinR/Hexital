from typing import List

from hexital.core.candle import Candle
from hexital.core.candlestick_type import CandlestickType


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

    def convert_candle(self, candle: Candle, candles: List[Candle], index: int):
        new_close = (candle.open + candle.high + candle.low + candle.close) / 4

        if index == 0:
            candle.open = (candle.open + candle.close) / 2
        else:
            candle.open = (candles[index - 1].open + candles[index - 1].close) / 2

        candle.high = max(candle.open, candle.high, new_close)
        candle.low = min(candle.open, candle.low, new_close)

        candle.close = new_close
