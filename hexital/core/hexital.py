import importlib
from copy import deepcopy
from datetime import timedelta
from typing import Dict, List, Optional

from hexital.core.candle import Candle
from hexital.core.indicator import Indicator
from hexital.exceptions import InvalidIndicator
from hexital.lib.candle_extension import collapse_candles_timeframe, reading_by_index

DEFAULT = "default"


class Hexital:
    name: str = None
    _candles: Dict[str, List[Candle]] = None
    _indicators: Dict[str, Indicator] = None
    description: Optional[str] = None
    timeframe_fill: bool = False
    candles_timerange: timedelta = None

    def __init__(
        self,
        name: str,
        candles: List[Candle],
        indicators: List[dict | Indicator] = None,
        description: Optional[str] = None,
        timeframe_fill: bool = False,
        candles_timerange: timedelta = None,
    ):
        self.name = name
        self._candles = {DEFAULT: deepcopy(candles) if isinstance(candles, list) else []}
        self._indicators = self._validate_indicators(indicators)
        self.description = description
        self.timeframe_fill = timeframe_fill
        self.candles_timerange = candles_timerange
        self._collapse_candles()
        self._candles_timerange()

    def _validate_indicators(
        self, indicators: List[dict | Indicator]
    ) -> Dict[str, Indicator]:
        indicator_module = importlib.import_module("hexital.indicators")
        pattern_module = importlib.import_module("hexital.analysis.patterns")
        valid_indicators = {}

        if not indicators:
            return {}

        for indicator in indicators:
            if isinstance(indicator, Indicator):
                valid_indicators[indicator.name] = indicator
            elif isinstance(indicator, dict):
                indicator_name = indicator.get("indicator")
                pattern_name = indicator.get("pattern")

                if indicator_name is None and pattern_name is None:
                    raise InvalidIndicator(
                        f"Dict Indicator missing 'indicator' or 'pattern' name: {indicator}"
                    )

                if indicator_name:
                    indicator_class = getattr(indicator_module, indicator_name, None)
                    if indicator_class is not None:
                        arguments = indicator.copy()
                        arguments.pop("indicator")
                        new_indicator = indicator_class(**arguments)
                        valid_indicators[new_indicator.name] = new_indicator
                    else:
                        raise InvalidIndicator(
                            f"Indicator {indicator_name} does not exist"
                        )
                elif pattern_name and isinstance(pattern_name, str):
                    pattern_func = getattr(pattern_module, pattern_name, None)
                    pattern_class = getattr(indicator_module, "Pattern", None)
                    if pattern_func is not None:
                        arguments = indicator.copy()
                        arguments.pop("pattern")
                        new_indicator = pattern_class(pattern=pattern_func, **arguments)
                        valid_indicators[new_indicator.name] = new_indicator
                    else:
                        raise InvalidIndicator(f"Indicator {pattern_name} does not exist")
                elif pattern_name and callable(pattern_name):
                    pattern_class = getattr(indicator_module, "Pattern", None)
                    arguments = indicator.copy()
                    arguments.pop("pattern")
                    new_indicator = pattern_class(pattern=pattern_name, **arguments)
                    valid_indicators[new_indicator.name] = new_indicator
                else:
                    raise InvalidIndicator(f"Indicator {pattern_name} does not exist")

        for indicator in valid_indicators.values():
            if indicator.timeframe is not None:
                if self._candles.get(indicator.timeframe) is None:
                    self._candles[indicator.timeframe] = deepcopy(self._candles[DEFAULT])
                indicator.candles = self._candles[indicator.timeframe]
            else:
                indicator.candles = self._candles[DEFAULT]

        return valid_indicators

    def _collapse_candles(self):
        for timeframe, candles in self._candles.items():
            if timeframe == DEFAULT:
                continue
            candles.extend(
                collapse_candles_timeframe(candles, timeframe, self.timeframe_fill)
            )

    def _candles_timerange(self):
        if self.candles_timerange is None:
            return

        for candles in self._candles.values():
            if not candles:
                return
            latest = candles[-1].timestamp
            while candles[0].timestamp < latest - self.candles_timerange:
                candles.pop(0)

    def candles(self, timeframe: Optional[str] = DEFAULT) -> List[Candle]:
        return self._candles.get(timeframe, DEFAULT)

    def candles_all(self) -> Dict[str, List[Candle]]:
        return self._candles

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

    def has_reading(self, name: str) -> bool:
        """Checks if the given Indicator has a valid reading in latest Candle"""
        return bool(self.reading(name))

    def reading(self, name: str, index: int = -1) -> float | dict | None:
        """Attempts to retrieve a reading with a given Indicator name.
        `name` can use '.' to find nested reading, E.G `MACD_12_26_9.MACD`
        """
        reading = reading_by_index(self._candles[DEFAULT], name, index=index)
        if reading is None:
            for candles in self._candles.values():
                reading = reading_by_index(candles, name, index=index)
                if reading is not None:
                    break

        return reading

    def prev_reading(self, name: str = None) -> float | dict | None:
        return self.reading(name, index=-2)

    def reading_as_list(self, name: Optional[str] = None) -> List[float | dict]:
        """Find given indicator and returns the readings as a list
        Full Name of the indicator E.G EMA_12"""
        if self._indicators.get(name):
            return self._indicators[name].as_list
        return []

    def add_indicator(self, indicator: Indicator | List[Indicator]):
        """Add's a new indicator to `Hexital` strategy.
        This accept either `Indicator` datatypes or dict string versions to be packed.
        `add_indicator(SMA(period=10))` or `add_indicator({"indicator": "SMA", "period": 10})`
        Does not automatically calculates readings."""
        if not isinstance(indicator, list):
            indicator = [indicator]

        for valid_indicator in self._validate_indicators(indicator).values():
            self._indicators[valid_indicator.name] = valid_indicator
        self._collapse_candles()

    def get_indicator(self, name: str) -> Indicator | None:
        """Searches hexital's indicator's and Returns the Indicator object itself."""
        return self._indicators.get(name)

    def remove_indicator(self, name: str):
        """Removes an indicator from running within hexital"""
        self.purge(name)
        self._indicators.pop(name, None)

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

        for existing_candles in self._candles.values():
            existing_candles.extend(deepcopy(candles_))

        self._collapse_candles()
        self._candles_timerange()

        self.calculate()

    def purge(self, name: Optional[str] = None) -> bool:
        """Takes Indicator name and removes all readings for said indicator.
        Indicator name must be exact"""
        for indicator_name, indicator in self._indicators.items():
            if name is None or indicator_name == name:
                indicator.purge()
                return True
        return False

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
