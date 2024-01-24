import importlib
from copy import deepcopy
from datetime import timedelta
from typing import Dict, List, Optional

from hexital.core.candle import Candle
from hexital.core.candle_manager import DEFAULT_CANDLES, CandleManager
from hexital.core.indicator import Indicator
from hexital.exceptions import InvalidAnalysis, InvalidIndicator
from hexital.utils.candlesticks import (
    reading_by_index,
)


class Hexital:
    name: str
    _candles: Dict[str, CandleManager]
    _indicators: Dict[str, Indicator]
    description: Optional[str] = None
    timeframe_fill: bool = False
    candles_lifespan: Optional[timedelta] = None

    def __init__(
        self,
        name: str,
        candles: List[Candle],
        indicators: Optional[List[dict | Indicator]] = None,
        description: Optional[str] = None,
        timeframe_fill: bool = False,
        candles_lifespan: Optional[timedelta] = None,
    ):
        self.name = name

        self._candles = {
            DEFAULT_CANDLES: CandleManager(
                deepcopy(candles) if isinstance(candles, list) else [],
                DEFAULT_CANDLES,
                candles_lifespan=candles_lifespan,
            )
        }

        self.description = description
        self.timeframe_fill = timeframe_fill
        self.candles_lifespan = candles_lifespan

        self._indicators = self._validate_indicators(indicators) if indicators else {}

    def _validate_indicators(self, indicators: List[dict | Indicator]) -> Dict[str, Indicator]:
        if not indicators:
            return {}

        valid_indicators = {}

        for indicator in indicators:
            if isinstance(indicator, Indicator):
                valid_indicators[indicator.name] = indicator
                continue

            if not isinstance(indicator, dict):
                raise InvalidIndicator(
                    f"Indicator type invalid 'indicator' must be a dict or Indicator type: {indicator}"
                )

            new_indicator = self._build_indicator(indicator)
            valid_indicators[new_indicator.name] = new_indicator

        for indicator in valid_indicators.values():
            if not indicator.timeframe:
                indicator.candle_manager = self._candles[DEFAULT_CANDLES]
                continue

            if not self._candles.get(indicator.timeframe):
                self._candles[indicator.timeframe] = CandleManager(
                    deepcopy(self._candles[DEFAULT_CANDLES]).candles,
                    indicator.timeframe,
                    self.candles_lifespan,
                    indicator.timeframe,
                    self.timeframe_fill,
                )
            indicator.candle_manager = self._candles[indicator.timeframe]

        return valid_indicators

    def _build_indicator(self, raw_indicator: dict) -> Indicator:
        indicator_module = importlib.import_module("hexital.indicators")
        amorph_class = getattr(indicator_module, "Amorph")

        if raw_indicator.get("indicator"):
            indicator_name = raw_indicator.pop("indicator")

            try:
                indicator_class = getattr(indicator_module, indicator_name)
            except AttributeError:
                raise InvalidIndicator(f"Indicator {indicator_name} does not exist")

            return indicator_class(**raw_indicator)

        elif raw_indicator.get("analysis") and isinstance(raw_indicator.get("analysis"), str):
            name = raw_indicator.pop("analysis")
            pattern_module = importlib.import_module("hexital.analysis.patterns")
            movement_module = importlib.import_module("hexital.analysis.movement")

            pattern_func = getattr(pattern_module, name, None)
            analysis_func = getattr(movement_module, name, pattern_func)
            if not analysis_func:
                raise InvalidAnalysis(f"analysis {name} does not exist in patterns or movements")

            return amorph_class(analysis=analysis_func, **raw_indicator)

        elif raw_indicator.get("analysis") and callable(raw_indicator.get("analysis")):
            method_name = raw_indicator.pop("analysis")
            return amorph_class(analysis=method_name, **raw_indicator)
        else:
            raise InvalidAnalysis(
                f"Dict Indicator missing 'indicator' or 'analysis' name, not: {raw_indicator}"
            )

    def candles(self, timeframe: Optional[str] = None) -> List[Candle]:
        if timeframe and self._candles.get(timeframe, False):
            return self._candles[timeframe].candles
        return self._candles[DEFAULT_CANDLES].candles

    def candles_all(self) -> Dict[str, List[Candle]]:
        return {name: manager.candles for name, manager in self._candles.items()}

    @property
    def timeframes(self) -> List[str]:
        return list(self._candles.keys())

    @property
    def indicators(self) -> Dict[str, Indicator]:
        """Simply get's a list of all the Indicators within Hexital strategy"""
        return self._indicators

    @property
    def indicator_settings(self) -> List[dict]:
        """Simply get's a list of all the Indicators within Hexital strategy"""
        return [indicator.settings for indicator in self._indicators.values()]

    def indicator(self, name: str) -> Indicator | None:
        for indicator_name, indicator in self._indicators.items():
            if name in indicator_name:
                return indicator
        return None

    def has_reading(self, name: Optional[str]) -> bool:
        """Checks if the given Indicator has a valid reading in latest Candle"""
        return bool(self.reading(name))

    def reading(self, name: Optional[str], index: int = -1) -> float | dict | None:
        """Attempts to retrieve a reading with a given Indicator name.
        `name` can use '.' to find nested reading, E.G `MACD_12_26_9.MACD`
        """
        name = name if name else self.name
        reading = reading_by_index(self._candles[DEFAULT_CANDLES].candles, name, index=index)

        if reading is not None:
            return reading

        for candle_manager in self._candles.values():
            reading = reading_by_index(candle_manager.candles, name, index=index)
            if reading is not None:
                return reading

        return None

    def prev_reading(self, name: Optional[str] = None) -> float | dict | None:
        return self.reading(name, index=-2)

    def reading_as_list(self, name: Optional[str] = None) -> List[float | dict | None]:
        """Find given indicator and returns the readings as a list
        Full Name of the indicator E.G EMA_12"""
        name = name if name else self.name
        if self._indicators.get(name):
            return self._indicators[name].as_list
        return []

    def add_indicator(self, indicator: Indicator | List[Indicator] | Dict[str, str]):
        """Add's a new indicator to `Hexital` strategy.
        This accept either `Indicator` datatypes or dict string versions to be packed.
        `add_indicator(SMA(period=10))` or `add_indicator({"indicator": "SMA", "period": 10})`
        Does not automatically calculates readings."""
        indicators = indicator if isinstance(indicator, list) else [indicator]

        for valid_indicator in self._validate_indicators(indicators).values():
            self._indicators[valid_indicator.name] = valid_indicator

    def get_indicator(self, name: str) -> Indicator | None:
        """Searches hexital's indicator's and Returns the Indicator object itself."""
        return self._indicators.get(name)

    def remove_indicator(self, name: str):
        """Removes an indicator from running within hexital"""
        self.purge(name)
        self._indicators.pop(name, None)

    def append(self, candles: Candle | List[Candle] | dict | List[dict] | list | List[list]):
        for candle_manager in self._candles.values():
            candle_manager.append(deepcopy(candles))

        self.calculate()

    def purge(self, name: Optional[str] = None):
        """Takes Indicator name and removes all readings for said indicator.
        Indicator name must be exact"""
        for indicator_name, indicator in self._indicators.items():
            if name is None or (name and name in indicator_name):
                indicator.purge()

    def calculate(self, name: Optional[str] = None):
        """Calculates all the missing indicator readings."""
        for indicator_name, indicator in self._indicators.items():
            if name is None or indicator_name == name:
                indicator.calculate()

    def recalculate(self, name: Optional[str] = None):
        """Purge's all indicator reading's and re-calculates them all,
        ideal for changing an indicator parameters midway."""
        self.purge(name)
        self.calculate(name)
