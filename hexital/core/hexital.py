from copy import deepcopy
from datetime import timedelta
from typing import Dict, List, Optional, Set

from hexital.analysis import MOVEMENT_MAP, PATTERN_MAP, movement, patterns
from hexital.core.candle import Candle
from hexital.core.candle_manager import DEFAULT_CANDLES, CandleManager
from hexital.core.candlestick_type import CandlestickType
from hexital.core.indicator import Indicator
from hexital.exceptions import (
    InvalidAnalysis,
    InvalidIndicator,
    InvalidTimeFrame,
    MissingIndicator,
    MixedTimeframes,
)
from hexital.indicators import INDICATOR_MAP
from hexital.utils.candles import reading_by_index
from hexital.utils.candlesticks import validate_candlesticktype
from hexital.utils.timeframe import TimeFrame, validate_timeframe


class Hexital:
    name: str
    _candles: Dict[str, CandleManager]
    _indicators: Dict[str, Indicator]
    description: Optional[str] = None
    timeframe: Optional[str] = None
    timeframe_fill: bool = False
    candles_lifespan: Optional[timedelta] = None
    candlestick_type: Optional[CandlestickType] = None

    def __init__(
        self,
        name: str,
        candles: List[Candle],
        indicators: Optional[List[dict | Indicator]] = None,
        description: Optional[str] = None,
        timeframe: Optional[str | TimeFrame] = None,
        timeframe_fill: bool = False,
        candles_lifespan: Optional[timedelta] = None,
        candlestick_type: Optional[CandlestickType | str] = None,
    ):
        self.name = name
        self.description = description

        if timeframe:
            self.timeframe = validate_timeframe(timeframe)
        self.timeframe_fill = timeframe_fill
        self.candles_lifespan = candles_lifespan

        if candlestick_type:
            self.candlestick_type = validate_candlesticktype(candlestick_type)

        self._candles = {
            DEFAULT_CANDLES: CandleManager(
                candles if isinstance(candles, list) else [],
                candles_lifespan=self.candles_lifespan,
                timeframe=self.timeframe,
                timeframe_fill=self.timeframe_fill,
                candlestick_type=self.candlestick_type,
            )
        }

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
            manager = CandleManager(
                [],
                candles_lifespan=self.candles_lifespan,
                timeframe=indicator.timeframe if indicator.timeframe else self.timeframe,
                timeframe_fill=self.timeframe_fill,
                candlestick_type=self.candlestick_type,
            )

            if manager == self._candles[DEFAULT_CANDLES]:
                indicator.candle_manager = self._candles[DEFAULT_CANDLES]
            elif manager.name in self._candles:
                indicator.candle_manager = self._candles[manager.name]
            else:
                self._candles[manager.name] = manager
                manager.append(deepcopy(self._candles[DEFAULT_CANDLES]).candles)
                indicator.candle_manager = self._candles[manager.name]

        return valid_indicators

    def _build_indicator(self, raw_indicator: dict) -> Indicator:
        analysis_map = PATTERN_MAP | MOVEMENT_MAP
        amorph_class = INDICATOR_MAP["Amorph"]

        if raw_indicator.get("indicator"):
            indicator_name = raw_indicator.pop("indicator")

            if INDICATOR_MAP.get(indicator_name):
                indicator_class = INDICATOR_MAP[indicator_name]
                return indicator_class(**raw_indicator)
            else:
                raise InvalidIndicator(f"Indicator {indicator_name} does not exist")

        elif raw_indicator.get("analysis") and isinstance(raw_indicator.get("analysis"), str):
            analysis_name = raw_indicator.pop("analysis")
            if not analysis_map.get(analysis_name):
                raise InvalidAnalysis(
                    f"analysis {analysis_name} does not exist in patterns or movements"
                )

            return amorph_class(analysis=analysis_map[analysis_name], **raw_indicator)

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
    def timeframes(self) -> Set[str]:
        return {str(manager.timeframe) for manager in self._candles.values()}

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

    def get_indicator(self, name: str) -> Indicator | None:
        """Searches hexital's indicator's and Returns the Indicator object itself."""
        return self._indicators.get(name)

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

    def _find_indicator(self, indicator: str) -> CandleManager | None:
        for manager in self._candles.values():
            if not manager.candles:
                return manager
            elif manager.find_indicator(indicator):
                return manager

        return None

    def _verify_indicators(
        self, indicator: str, indicator_two: Optional[str] = None
    ) -> List[Candle]:
        manager = self._find_indicator(indicator)

        if not manager and indicator in self._indicators:
            return []
        elif manager and not indicator_two:
            return manager.candles

        if not indicator_two or not manager:
            raise MissingIndicator("Cannot find Indicator: %s" % indicator)

        manager_two = self._find_indicator(indicator_two)

        if not manager_two:
            raise MissingIndicator("Cannot find Indicator: %s" % indicator_two)

        for manager in self._candles.values():
            if manager.find_indicator(indicator) and manager.find_indicator(indicator_two):
                return manager.candles

        raise MixedTimeframes(
            "Cannot find {%s} and {%s} within same timeframe" % (indicator, indicator_two)
        )

    def above(self, indicator: str, indicator_two: str, index: int = -1) -> bool:
        candles = self._verify_indicators(indicator, indicator_two)
        return movement.above(candles, indicator, indicator_two, index)

    def below(self, indicator: str, indicator_two: str, index: int = -1) -> bool:
        candles = self._verify_indicators(indicator, indicator_two)
        return movement.below(candles, indicator, indicator_two, index)

    def cross(self, indicator: str, indicator_two: str, length: int = 1, index: int = -1) -> bool:
        candles = self._verify_indicators(indicator, indicator_two)
        return movement.cross(candles, indicator, indicator_two, length, index)

    def crossover(
        self, indicator: str, indicator_two: str, length: int = 1, index: int = -1
    ) -> bool:
        candles = self._verify_indicators(indicator, indicator_two)
        return movement.crossover(candles, indicator, indicator_two, length, index)

    def crossunder(
        self, indicator: str, indicator_two: str, length: int = 1, index: int = -1
    ) -> bool:
        candles = self._verify_indicators(indicator, indicator_two)
        return movement.crossunder(candles, indicator, indicator_two, length, index)

    def rising(self, name: str, length: int = 4, index: int = -1) -> bool:
        candles = self._verify_indicators(name)
        return movement.rising(candles, name, length, index)

    def falling(self, name: str, length: int = 4, index: int = -1) -> bool:
        candles = self._verify_indicators(name)
        return movement.falling(candles, name, length, index)

    def mean_rising(self, name: str, length: int = 4, index: int = -1) -> bool:
        candles = self._verify_indicators(name)
        return movement.mean_rising(candles, name, length, index)

    def mean_falling(self, name: str, length: int = 4, index: int = -1) -> bool:
        candles = self._verify_indicators(name)
        return movement.mean_falling(candles, name, length, index)

    def highest(self, name: str, length: int = 4, index: int = -1) -> float:
        candles = self._verify_indicators(name)
        return movement.highest(candles, name, length, index)

    def lowest(self, name: str, length: int = 4, index: int = -1) -> float:
        candles = self._verify_indicators(name)
        return movement.lowest(candles, name, length, index)

    def highestbar(self, name: str, length: int = 4, index: int = -1) -> int | None:
        candles = self._verify_indicators(name)
        return movement.highestbar(candles, name, length, index)

    def lowestbar(self, name: str, length: int = 4, index: int = -1) -> int | None:
        candles = self._verify_indicators(name)
        return movement.lowestbar(candles, name, length, index)

    def doji(
        self,
        timeframe: str | TimeFrame,
        length: int = 10,
        lookback: Optional[int] = None,
        asint: bool = False,
        index: Optional[int] = None,
    ) -> bool | int:
        manager = self._candles.get(validate_timeframe(timeframe))
        if not manager:
            raise InvalidTimeFrame(f"Timeframe {timeframe} not found")
        return patterns.doji(
            manager.candles, length=length, lookback=lookback, asint=asint, index=index
        )

    def hammer(
        self,
        timeframe: str | TimeFrame,
        length: int = 10,
        lookback: Optional[int] = None,
        asint: bool = False,
        index: Optional[int] = None,
    ) -> bool | int:
        manager = self._candles.get(validate_timeframe(timeframe))
        if not manager:
            raise InvalidTimeFrame(f"Timeframe {timeframe} not found")
        return patterns.hammer(
            manager.candles, length=length, lookback=lookback, asint=asint, index=index
        )
