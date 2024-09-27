from abc import ABC, abstractmethod
from typing import List

from hexital.core.candle import Candle


class CandlestickType(ABC):
    name: str = "N/A"
    acronym: str = "NA"

    def __init__(self):
        return

    @abstractmethod
    def convert_candle(self, candle: Candle, candles: List[Candle], index: int): ...

    def conversion(self, candles: List[Candle]):
        for index in range(self._find_conv_index(candles), len(candles)):
            candle = candles[index]
            candle.save_clean_values()
            self.convert_candle(candle, candles, index)
            candle.reset_candle()
            candle.tag = self.name

    def _find_conv_index(self, candles: List[Candle]) -> int:
        if len(candles) == 0 or not candles[0].tag:
            return 0

        for index in range(len(candles) - 1, 0, -1):
            if self.name == candles[index].tag:
                return index + 1
        return len(candles)
