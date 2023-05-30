from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List

from hexital.types.ohlcv import Candle


@dataclass(kw_only=True)
class Indicator(ABC):
    candles: List[Candle]
    indicator_name: str = None
    override_name: str = None
    _round_value: int = 4
    _output_indicator_name: str = ""

    def __post_init__(self):
        self._output_indicator_name = (
            self.override_name if self.override_name else self._generate_name()
        )
        self.calculate()

    @property
    def name(self):
        """The indicator name that will be saved into the Candles"""
        return self._output_indicator_name

    @property
    def round_by(self):
        return self._round_value

    @round_by.setter
    def round_by(self, value):
        self._round_value = value

    @abstractmethod
    def _generate_name(self):
        pass

    @abstractmethod
    def _calculate_new_value(self, index: int = -1) -> float | None:
        pass

    def calculate(self):
        """Calculate the TA values, will calculate for all the Candles,
        where this indicator is missing"""
        for index in range(self._find_starting_index(), len(self.candles)):
            if self._output_indicator_name not in self.candles[index].hex_ta:
                value = self._calculate_new_value(index=index)

                if value:
                    value = round(value, self._round_value)

                self.candles[index].hex_ta[self._output_indicator_name] = value

    def _find_starting_index(self) -> int:
        """Optimisation method, to find where to start calculating the indicator from"""
        if self._output_indicator_name not in self.candles[0].hex_ta:
            return 0

        for index in range(len(self.candles) - 1, 0, -1):
            if self._output_indicator_name in self.candles[index].hex_ta:
                return index + 1
        return 0

    def get_newest(self) -> float | dict:
        """Get's this newest value of this indicator"""
        return self.candles[-1].ta.get(self._output_indicator_name, None)

    def get_prev(self, index: int = None) -> float | dict:
        """Get's this Prev value of this indicator.
        if no index is specified gets prev latest"""
        if index is None:
            index = len(self.candles) - 1
        return self.get_indicator(self.candles[index - 1], self._output_indicator_name)

    def get_indicator(
        self, candle: Candle, name: str = None, default=None
    ) -> float | dict:
        """Simple method to an indicator from a candle, regardless of it's location"""
        if not name:
            name = self._output_indicator_name
        try:
            return getattr(candle, name)
        except AttributeError:
            return candle.hex_ta.get(name, default)

    def get_as_list(self) -> List[float | dict]:
        """Gathers the indicator for all candles as a list"""
        return [candle.hex_ta.get(self._output_indicator_name) for candle in self.candles]

    @property
    def has_output_value(self) -> bool:
        """Simple boolean to state if values are being generated yet in the candles"""
        return self.candles[-1].hex_ta.get(self._output_indicator_name) is not None
