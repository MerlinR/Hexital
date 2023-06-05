from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from itertools import chain
from typing import Dict, List, Union

from hexital.types.ohlcv import Candle


@dataclass(kw_only=True)
class Indicator(ABC):
    candles: List[Candle] = field(default_factory=list)
    indicator_name: str = None
    override_name: str = None
    name_postix: str = None
    round_value: int = 4
    _output_name: str = ""
    _sub_indicators: List[Indicator] = field(default_factory=list)
    _managed_indicators: Dict[str, Indicator] = field(default_factory=dict)
    _sub_indicator: bool = False

    def __post_init__(self):
        if self.override_name:
            self._output_name = self.override_name
        elif self.name_postix:
            self._output_name = f"{self._generate_name()}_{self.name_postix}"
        else:
            self._output_name = self._generate_name()
        self._initialise()

    def _initialise(self):
        pass

    @abstractmethod
    def _generate_name(self):
        pass

    @property
    def name(self):
        """The indicator name that will be saved into the Candles"""
        return self._output_name

    @property
    def value(self) -> float | dict:
        """Get's this newest value of this indicator"""
        return self.candles[-1][self._output_name]

    @property
    def sub_indicator(self):
        return self._sub_indicator

    @sub_indicator.setter
    def sub_indicator(self, value: bool):
        self._sub_indicator = value

    @property
    def purge(self):
        for candle in self.candles:
            candle.indicators = {}

    @property
    def has_value(self) -> bool:
        """Simple boolean to state if values are being generated yet in the candles"""
        if len(self.candles) == 0:
            return False
        return self.get_indicator_by_index(-1) is not None

    def _set_value(self, index: int, value: Union[float, dict]):
        if self.sub_indicator:
            self.candles[index].sub_indicators[self.name] = value
        else:
            self.candles[index].indicators[self.name] = value

    @abstractmethod
    def _calculate_new_value(self, index: int = -1) -> float | dict | None:
        pass

    def calculate(self):
        """Calculate the TA values, will calculate for all the Candles,
        where this indicator is missing"""
        for indicator in self._sub_indicators:
            indicator.calculate()

        for index in range(self._find_starting_index(), len(self.candles)):
            if self.get_indicator_by_index(index) is None:
                value = self._round_values(self._calculate_new_value(index=index))
                self._set_value(index, value)

    def calculate_index(self, index: int, to_index: int = None):
        """Calculate the TA values, will calculate a index range the Candles,
        where this indicator is missing"""
        for i in range(index, to_index if to_index else index + 1):
            value = self._round_values(self._calculate_new_value(index=i))
            self._set_value(i, value)

    def _round_values(self, values: float | Dict[str, float]) -> float | Dict[str, float]:
        if isinstance(values, dict):
            for key, val in values.items():
                if val is not None:
                    values[key] = round(val, self.round_value)
        elif isinstance(values, float):
            values = round(values, self.round_value)

        return values

    def _find_starting_index(self) -> int:
        """Optimisation method, to find where to start calculating the indicator from
        Searches from newest to oldest to find the first candle without the indicator
        """
        if self.name not in self.candles[0].indicators:
            return 0

        for index in range(len(self.candles) - 1, 0, -1):
            if self.name in self.candles[index].indicators:
                return index + 1
        return 0

    def add_sub_indicator(self, indicator: Indicator):
        """Adds sub indicator, this will auto calculate with indicator"""
        indicator.sub_indicator = True
        self._sub_indicators.append(indicator)

    def add_managed_indicator(self, name: str, indicator: Indicator):
        """Adds managed sub indicator, this will not auto calculate with indicator"""
        indicator.sub_indicator = True
        self._managed_indicators[name] = indicator

    def get_managed_indictor(self, name: str) -> Indicator:
        return self._managed_indicators.get(name)

    def prev_exists(self, index: int = None) -> bool:
        if index == 0:
            return False
        return self.get_indicator_by_index(index - 1) is not None

    def get_indicator_by_index(
        self, index: int = None, name: str = None
    ) -> float | dict | None:
        """Simple method to get an indicator value from it's index,
        regardless of it's location"""
        if index is None:
            index = len(self.candles) - 1
        if not name:
            name = self.name

        return self.get_indicator_by_candle(self.candles[index], name)

    def get_indicator_by_candle(
        self, candle: Candle, name: str = None
    ) -> float | dict | None:
        """Simple method to get an indicator value from a candle,
        regardless of it's location"""
        if not name:
            name = self.name

        if "." in name:
            main_name, nested_name = name.split(".")
            value = self._get_nested_indicator(candle, main_name, nested_name)
            if value:
                return value

        if getattr(candle, name, None) is not None:
            return getattr(candle, name)

        if name in candle.indicators:
            return candle.indicators[name]

        if name in candle.sub_indicators:
            return candle.sub_indicators[name]

        for key, value in chain(candle.indicators.items(), candle.sub_indicators.items()):
            if name in key:
                return value

        return None

    def _get_nested_indicator(
        self, candle: Candle, name: str, nested_name: str
    ) -> float | None:
        if name in candle.indicators:
            if isinstance(candle.indicators[name], dict):
                return candle.indicators[name].get(nested_name)
            return candle.indicators[name]

        if name in candle.sub_indicators:
            if isinstance(candle.sub_indicators[name], dict):
                return candle.sub_indicators[name].get(nested_name)
            return candle.sub_indicators[name]

        for key, value in chain(candle.indicators.items(), candle.sub_indicators.items()):
            if name in key:
                if isinstance(value, dict):
                    return value.get(nested_name)
                return value
        return None

    def get_indicator_count(self, name: str = None) -> int:
        """Returns how many instance of the given indicator exist"""
        if not name:
            name = self.name
        count = 0
        for candle in self.candles:
            if self.get_indicator_by_candle(candle, name):
                count += 1

        return count

    def get_as_list(self, name: str = None) -> List[float | dict]:
        """Gathers the indicator for all candles as a list"""
        if not name:
            name = self.name
        return [candle.indicators.get(name) for candle in self.candles]

    def get_indicator_period(
        self, period: int, index: int = None, name: str = None
    ) -> bool:
        """Will return True if the given indicator goes back as far as amount,
        It's true if exactly or more than. Period will be period -1"""
        if index is None:
            index = len(self.candles) - 1
        if name is None:
            name = self.name
        period -= 1

        if (index - period) < 0:
            return False

        # Checks 3 points along period to verify values exist
        return all(
            self.get_indicator_by_index(index - int(x), name)
            for x in [
                period,
                period / 2,
                0,
            ]
        )
