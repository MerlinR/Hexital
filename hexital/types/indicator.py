from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List

from hexital.types.ohlcv import Candle


@dataclass(kw_only=True)
class Indicator(ABC):
    candles: List[Candle]
    _round_value: int = 4
    _output_indicator_name: str = ""

    def __post_init__(self):
        self._output_indicator_name = self._gen_name()
        self.calculate()

    @property
    def round_by(self):
        return self._round_value

    @round_by.setter
    def round_by(self, value):
        self._round_value = value

    @abstractmethod
    def _gen_name(self):
        pass

    @abstractmethod
    def _calculate_new_value(self, index: int = -1) -> float | None:
        pass

    def calculate(self):
        for index in range(self._find_starting_index(), len(self.candles)):
            if self._output_indicator_name not in self.candles[index].hex_ta:
                value = self._calculate_new_value(index=index)

                if value:
                    value = round(value, self._round_value)

                self.candles[index].hex_ta[self._output_indicator_name] = value

    def get_prev_indicator(self, index: int, name: str = None) -> float:
        if not name:
            name = self._output_indicator_name
        return self.get_indicator(self.candles[index - 1], name)

    def get_indicator(self, candle: Candle, name: str = None, default=None) -> float:
        if not name:
            name = self._output_indicator_name
        try:
            return getattr(candle, name)
        except AttributeError:
            return candle.hex_ta.get(name, default)

    def _find_starting_index(self) -> int:
        if self._output_indicator_name not in self.candles[0].hex_ta:
            return 0

        for index in range(len(self.candles) - 1, 0, -1):
            if self._output_indicator_name in self.candles[index].hex_ta:
                return index + 1
        return 0
