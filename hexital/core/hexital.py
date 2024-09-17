from copy import copy, deepcopy
from datetime import timedelta
from importlib import import_module
from typing import Dict, List, Optional, Set

from hexital.core.candle import Candle
from hexital.core.candle_manager import DEFAULT_CANDLES, CandleManager
from hexital.core.candlestick_type import CandlestickType
from hexital.core.indicator import Indicator
from hexital.exceptions import (
    InvalidAnalysis,
    InvalidIndicator,
)
from hexital.indicators.amorph import Amorph
from hexital.utils.candles import reading_by_index
from hexital.utils.candlesticks import validate_candlesticktype
from hexital.utils.timeframe import TimeFrame, convert_timeframe_to_timedelta, timedelta_to_str


class Hexital:
    name: str
    _candles: Dict[str, CandleManager]
    _indicators: Dict[str, Indicator]
    description: Optional[str] = None
    _timeframe: Optional[timedelta] = None
    timeframe_fill: bool = False
    candles_lifespan: Optional[timedelta] = None
    candlestick_type: Optional[CandlestickType] = None

    def __init__(
        self,
        name: str,
        candles: List[Candle],
        indicators: Optional[List[dict | Indicator]] = None,
        description: Optional[str] = None,
        timeframe: Optional[str | TimeFrame | timedelta | int] = None,
        timeframe_fill: bool = False,
        candles_lifespan: Optional[timedelta] = None,
        candlestick_type: Optional[CandlestickType | str] = None,
    ):
        self.name = name
        self.description = description

        self._timeframe = convert_timeframe_to_timedelta(timeframe)
        self.timeframe_fill = timeframe_fill
        self.candles_lifespan = candles_lifespan

        if candlestick_type:
            self.candlestick_type = validate_candlesticktype(candlestick_type)

        self._candles = {
            DEFAULT_CANDLES: CandleManager(
                candles if isinstance(candles, list) else [],
                candles_lifespan=self.candles_lifespan,
                timeframe=self._timeframe,
                timeframe_fill=self.timeframe_fill,
                candlestick_type=self.candlestick_type,
            )
        }
        self._candles[DEFAULT_CANDLES].name = DEFAULT_CANDLES

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
            elif indicator.timeframe and indicator.timeframe in self._candles:
                indicator.candle_manager = self._candles[indicator.timeframe]
            else:
                manager = CandleManager(
                    deepcopy(self._candles[DEFAULT_CANDLES]).candles,
                    candles_lifespan=self.candles_lifespan,
                    timeframe=indicator._timeframe if indicator._timeframe else self._timeframe,
                    timeframe_fill=self.timeframe_fill,
                    candlestick_type=self.candlestick_type,
                )
                self._candles[manager.name] = manager
                indicator.candle_manager = self._candles[manager.name]

        return valid_indicators

    def _build_indicator(self, raw_indicator: dict) -> Indicator:
        indicator = copy(raw_indicator)

        if indicator.get("indicator"):
            indicator_name = indicator.pop("indicator")
            indicator_class = getattr(import_module("hexital.indicators"), indicator_name, None)

            if indicator_class:
                return indicator_class(**indicator)
            else:
                raise InvalidIndicator(f"Indicator {indicator_name} does not exist. [{indicator}]")

        elif indicator.get("analysis") and isinstance(indicator.get("analysis"), str):
            analysis_name = indicator.pop("analysis")
            analysis_class = getattr(import_module("hexital.analysis"), analysis_name, None)

            if not analysis_class:
                raise InvalidAnalysis(
                    f"analysis {analysis_name} does not exist in patterns or movements. [{indicator}]"
                )

            return Amorph(analysis=analysis_class, **indicator)

        elif indicator.get("analysis") and callable(indicator.get("analysis")):
            method_name = indicator.pop("analysis")
            return Amorph(analysis=method_name, **indicator)
        else:
            raise InvalidAnalysis(
                f"Dict Indicator missing 'indicator' or 'analysis' name, not: {raw_indicator}"
            )

    def candles(self, timeframe: Optional[str] = None) -> List[Candle]:
        if timeframe and self._candles.get(timeframe, False):
            return self._candles[timeframe].candles
        return self._candles[DEFAULT_CANDLES].candles

    def get_candles(self) -> Dict[str, List[Candle]]:
        return {name: manager.candles for name, manager in self._candles.items()}

    @property
    def timeframe(self) -> str | None:
        return timedelta_to_str(self._timeframe) if self._timeframe else None

    @property
    def timeframes(self) -> Set[str]:
        return {manager.name for manager in self._candles.values()}

    @property
    def indicators(self) -> Dict[str, Indicator]:
        """Simply get's a list of all the Indicators within Hexital strategy"""
        return self._indicators

    def indicator(self, name: str) -> Indicator:
        """Searches hexital's indicator's and Returns the Indicator object itself."""
        return self._indicators[name]

    @property
    def indicator_settings(self) -> List[dict]:
        """Simply get's a list of all the Indicators within Hexital strategy"""
        return [indicator.settings for indicator in self._indicators.values()]

    def has_reading(self, name: str) -> bool:
        """Checks if the given Indicator has a valid reading in latest Candle"""
        return bool(self.reading(name))

    def reading(self, name: str, index: int = -1) -> float | dict | None:
        """Attempts to retrieve a reading with a given Indicator name.
        `name` can use '.' to find nested reading, E.G `MACD_12_26_9.MACD`
        """
        reading = reading_by_index(self._candles[DEFAULT_CANDLES].candles, name, index=index)

        if reading is not None:
            return reading

        for candle_manager in self._candles.values():
            reading = reading_by_index(candle_manager.candles, name, index=index)
            if reading is not None:
                return reading

        return None

    def prev_reading(self, name: str) -> float | dict | None:
        return self.reading(name, index=-2)

    def reading_as_list(self, name: str) -> List[float | dict | None]:
        """Find given indicator and returns the readings as a list
        Full Name of the indicator E.G `EMA_12` OR `MACD_12_26_9.MACD`"""
        primary_name = name.split(".")[0]
        if self._indicators.get(primary_name):
            return self._indicators[primary_name].as_list(name)
        return []

    def add_indicator(
        self, indicator: Indicator | List[Indicator | Dict[str, str]] | Dict[str, str]
    ):
        """Add's a new indicator to `Hexital` strategy.
        This accept either `Indicator` datatypes or dict string versions to be packed.
        `add_indicator(SMA(period=10))` or `add_indicator({"indicator": "SMA", "period": 10})`
        Does not automatically calculates readings."""
        indicators = indicator if isinstance(indicator, list) else [indicator]

        for valid_indicator in self._validate_indicators(indicators).values():
            self._indicators[valid_indicator.name] = valid_indicator

    def remove_indicator(self, name: str):
        """Removes an indicator from running within hexital"""
        self.purge(name)
        self._indicators.pop(name, None)

    def append(self, candles: Candle | List[Candle] | dict | List[dict] | list | List[list]):
        for candle_manager in self._candles.values():
            candle_manager.append(candles)

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

    def calculate_index(self, name: Optional[str] = None, index: int = -1):
        """Calculate specific index for all or specific indicator readings."""
        for indicator_name, indicator in self._indicators.items():
            if name is None or indicator_name == name:
                indicator.calculate_index(index)

    def recalculate(self, name: Optional[str] = None):
        """Purge's all indicator reading's and re-calculates them all,
        ideal for changing an indicator parameters midway."""
        self.purge(name)
        self.calculate(name)
