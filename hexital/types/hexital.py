import importlib
from typing import List

from hexital.types.indicator import Indicator
from hexital.types.ohlcv import OHLCV
from hexital.utilities.ohlcv import reading_by_index


class Hexital:
    name: str = ""
    candles: List[OHLCV] = None
    _indicators: List[Indicator] = None
    description: str = ""

    def __init__(
        self,
        name: str,
        candles: List[OHLCV],
        indicators: List[dict | Indicator] = None,
        description: str = None,
    ):
        self.name = name
        self.candles = candles if candles else []
        self._indicators = self._verify_indicators(indicators)
        self.description = description

    def _verify_indicators(self, indicators: List[dict | Indicator]) -> List[Indicator]:
        module = importlib.import_module("hexital.indicators")
        valid_indicators = []

        if not indicators:
            return []

        for indic in indicators:
            if isinstance(indic, Indicator):
                valid_indicators.append(indic)
            elif isinstance(indic, dict):
                indicator_name = indic.pop("indicator", None)
                if indicator_name is None:
                    continue
                indicator_class = getattr(module, indicator_name, None)
                if indicator_class is not None:
                    valid_indicators.append(indicator_class(**indic))

        for indic in valid_indicators:
            indic.candles = self.candles

        return valid_indicators

    @property
    def indicators(self):
        return self._indicators

    def has_reading(self, indicator_name: str) -> bool:
        """Simple boolean to state if values are being generated yet in the candles"""
        for indicator in self._indicators:
            if indicator_name in indicator.name:
                return indicator.has_reading
        return False

    def read(self, indicator_name: str, index: int = -1) -> float | dict | None:
        return reading_by_index(self.candles, indicator_name, index=index)

    def reading_as_list(self, indicator_name: str = None) -> List[float | dict]:
        """Gathers the indicator for all candles as a list"""
        for indicator in self._indicators:
            if indicator_name is None or indicator_name in indicator.name:
                return indicator.get_as_list()
        return []

    def add_indicator(self, indicator: Indicator | List[Indicator]):
        """Add's a new indicator to the object. Does not automatically calculates readings"""
        if not isinstance(indicator, list):
            indicator = [indicator]

        for indi in self._verify_indicators(indicator):
            self._indicators.append(indi)

    def get_indicator(self, name: str) -> Indicator | None:
        """Searches hexital's indicator's and Returns the Indicator object itself."""
        for indicator in self._indicators:
            if name in indicator.name:
                return indicator
        return None

    def purge_readings(self, indicator_name: str = None) -> bool:
        """Takes Indicator name and removes all readings for said indicator.
        Indicator name must be exact"""
        for indicator in self._indicators:
            if indicator_name is None or indicator_name == indicator.name:
                indicator.purge_readings()
                return True
        return False

    def remove_indicator(self, indicator_name: str):
        """Removes an indicator from running within hexital"""
        self.purge_readings(indicator_name)
        for index, indic in enumerate(self._indicators):
            if indic.name == indicator_name:
                self._indicators.pop(index)

    def append(self, candle: OHLCV | dict):
        """Appends a OHLCV to candles and re-calculates"""
        if isinstance(candle, dict):
            new_ohlcv = OHLCV.from_dict(candle)
            if isinstance(new_ohlcv, OHLCV):
                self.candles.append()
        else:
            self.candles.append(candle)
        self.calculate()

    def calculate(self, indicator_name: str = None):
        """Calculates all the missing indicator readings."""
        for indicator in self._indicators:
            if indicator_name is None or indicator_name in indicator.name:
                indicator.calculate()

    def recalculate(self, indicator_name: str = None):
        """Purge's all indicator reading's and re-calculates them all,
        ideal for changing an indicator parameters midway."""
        self.purge_readings(indicator_name)
        self.calculate(indicator_name)
