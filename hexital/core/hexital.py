import importlib
from typing import List, Optional

from hexital.core.candle import Candle
from hexital.core.indicator import Indicator
from hexital.exceptions import InvalidIndicator
from hexital.lib.candle_extension import reading_by_index


class Hexital:
    name: str = ""
    candles: List[Candle] = None
    _indicators: List[Indicator] = None
    description: Optional[str] = None

    def __init__(
        self,
        name: str,
        candles: List[Candle],
        indicators: List[dict | Indicator] = None,
        description: Optional[str] = None,
    ):
        self.name = name
        self.candles = candles if isinstance(candles, list) else []
        self._indicators = self._validate_indicators(indicators)
        self.description = description

    def _validate_indicators(self, indicators: List[dict | Indicator]) -> List[Indicator]:
        module = importlib.import_module("hexital.indicators")
        valid_indicators = []

        if not indicators:
            return []

        for indicator in indicators:
            if isinstance(indicator, Indicator):
                valid_indicators.append(indicator)
            elif isinstance(indicator, dict):
                indicator_name = indicator.get("indicator")
                if indicator_name is None:
                    raise InvalidIndicator(
                        f"Dict Indicator missing 'indicator' name: {indicator}"
                    )
                indicator_class = getattr(module, indicator_name, None)
                if indicator_class is not None:
                    arguments = indicator.copy()
                    arguments.pop("indicator")
                    valid_indicators.append(indicator_class(**arguments))
                else:
                    raise InvalidIndicator(f"Indicator {indicator_name} does not exist")

        for indicator in valid_indicators:
            indicator.candles = self.candles

        return valid_indicators

    @property
    def indicators(self) -> List[Indicator]:
        """Simply get's a list of all the Indicators within Hexital stratergy"""
        return self._indicators

    def has_reading(self, indicator_name: str) -> bool:
        """Checks if the given Indicator has a valid reading in latest Candle"""
        for indicator in self._indicators:
            if indicator_name in indicator.name:
                return indicator.has_reading
        return False

    def reading(self, indicator_name: str, index: int = -1) -> float | dict | None:
        """Attempts to retrive a rading with a given Indicator name.
        `indicator_name` can use '.' to find nested reading, E.G `MACD_12_26_9.MACD`
        """
        return reading_by_index(self.candles, indicator_name, index=index)

    def reading_as_list(self, indicator_name: Optional[str] = None) -> List[float | dict]:
        """Find given indicator and returns the readings as a list
        Full Name of the indicator E.G EMA_12"""
        for indicator in self._indicators:
            if indicator_name is None or indicator_name in indicator.name:
                return indicator.as_list
        return []

    def add_indicator(self, indicator: Indicator | List[Indicator]):
        """Add's a new indicator to `Hexital` stratergy.
        This accept either `Indicator` datatypes or dict string versions to be packed.
        `add_indicator(SMA(period=10))` or `add_indicator({"indicator": "SMA", "period": 10})`
        Does not automatically calculates readings."""
        if not isinstance(indicator, list):
            indicator = [indicator]

        for valid_indicator in self._validate_indicators(indicator):
            self._indicators.append(valid_indicator)

    def get_indicator(self, name: str) -> Indicator | None:
        """Searches hexital's indicator's and Returns the Indicator object itself."""
        for indicator in self._indicators:
            if name in indicator.name:
                return indicator
        return None

    def remove_indicator(self, indicator_name: str):
        """Removes an indicator from running within hexital"""
        self.purge(indicator_name)
        for index, indic in enumerate(self._indicators):
            if indic.name == indicator_name:
                self._indicators.pop(index)

    def append(
        self, candles: Candle | List[Candle] | dict | List[dict] | list | List[list]
    ):
        candles_ = []
        if isinstance(candles, Candle):
            candles_.append(candles)
        elif isinstance(candles, dict):
            candles_.append(Candle.from_dict(candles))
        elif isinstance(candles, list):
            if isinstance(candles[0], Candle):
                candles_.extend(candles)
            elif isinstance(candles[0], dict):
                candles_.extend(Candle.from_dicts(candles))
            elif isinstance(candles[0], (float, int)):
                candles_.append(Candle.from_list(candles))
            elif isinstance(candles[0], list):
                candles_.extend(Candle.from_lists(candles))
            else:
                raise TypeError
        else:
            raise TypeError

        self.candles.extend(candles_)

        for indicator in self.indicators:
            if indicator.timeframe is not None:
                indicator.append(candles_)

        self.calculate()

    def purge(self, indicator_name: Optional[str] = None) -> bool:
        """Takes Indicator name and removes all readings for said indicator.
        Indicator name must be exact"""
        for indicator in self._indicators:
            if indicator_name is None or indicator_name == indicator.name:
                indicator.purge()
                return True
        return False

    def calculate(self, indicator_name: Optional[str] = None):
        """Calculates all the missing indicator readings."""
        for indicator in self._indicators:
            if indicator_name is None or indicator_name in indicator.name:
                indicator.calculate()

    def recalculate(self, indicator_name: Optional[str] = None):
        """Purge's all indicator reading's and re-calculates them all,
        ideal for changing an indicator parameters midway."""
        self.purge(indicator_name)
        self.calculate(indicator_name)
