from copy import copy
from datetime import timedelta
from importlib import import_module
from typing import Any, Dict, Generic, List, Optional, Sequence, Set, Tuple, TypeVar

from hexital.core import Reading
from hexital.core.candle import Candle
from hexital.core.candle_manager import DEFAULT_CANDLES, CandleManager, Candles
from hexital.core.candlestick_type import CandlestickType
from hexital.core.indicator import Indicator, NestedSource, Source
from hexital.core.indicator_collection import IndicatorCollection
from hexital.exceptions import InvalidAnalysis, InvalidIndicator
from hexital.indicators.amorph import Amorph
from hexital.utils.candles import reading_by_candle, reading_by_index
from hexital.utils.candlesticks import validate_candlesticktype
from hexital.utils.timeframe import (
    TimeFramesSource,
    convert_timeframe_to_timedelta,
    timedelta_to_str,
    timeframe_validation,
)


class Hexital:
    name: str
    description: Optional[str] = None
    timeframe_fill: bool = False
    candle_life: Optional[timedelta] = None
    candlestick: Optional[CandlestickType]

    _candle_map: Dict[str, CandleManager]
    _indicators: Dict[str, Indicator]
    _timeframe: Optional[timedelta]
    _default_name: str

    def __init__(
        self,
        name: str,
        candles: Sequence[Candle],
        indicators: Optional[Sequence[Dict[str, Any] | Indicator] | IndicatorCollection] = None,
        description: Optional[str] = None,
        timeframe: Optional[TimeFramesSource] = None,
        timeframe_fill: bool = False,
        candle_life: Optional[timedelta] = None,
        candlestick: Optional[CandlestickType | str] = None,
    ):
        self.name = name
        self.description = description

        self._timeframe = convert_timeframe_to_timedelta(timeframe)
        self.timeframe_fill = timeframe_fill
        self.candle_life = candle_life

        self.candlestick = validate_candlesticktype(candlestick) if candlestick else None

        manager = CandleManager(
            candles if isinstance(candles, list) else [],
            candle_life=self.candle_life,
            timeframe=self._timeframe,
            timeframe_fill=self.timeframe_fill,
            candlestick=self.candlestick,
        )

        self._default_name = manager.name
        self._candle_map = {manager.name: manager}

        if not indicators:
            self._indicators = {}
        elif isinstance(indicators, IndicatorCollection):
            self._indicators = self._validate_indicators(indicators.collection_list())
        else:
            self._indicators = self._validate_indicators(indicators)

    @property
    def timeframe(self) -> str | None:
        return timedelta_to_str(self._timeframe) if self._timeframe else None

    @property
    def timeframes(self) -> Set[str]:
        return {manager.name for manager in self._candle_map.values()}

    @property
    def indicators(self) -> Dict[str, Indicator]:
        return self._indicators

    def indicator(self, name: str) -> Indicator | None:
        """Searches hexital's indicator's and Returns the Indicator object itself."""
        return self._indicators.get(name)

    def exists(self, name: str) -> bool:
        """Checks if the given Indicator has a valid reading in latest Candle"""
        value = self.reading(name)
        if isinstance(value, dict):
            return any(v is not None for v in value.values())
        return value is not None

    def candles(self, name: Optional[TimeFramesSource] = None) -> List[Candle]:
        """Get a set of candles by using either a Timeframe or Indicator name"""
        name_ = name if name else self._default_name
        timeframe_name = self._parse_timeframe(name)

        name_ = timeframe_name if timeframe_name else name_

        if isinstance(name_, str) and self._candle_map.get(name_, False):
            return self._candle_map[name_].candles
        elif isinstance(name_, str):
            for manager in self._candle_map.values():
                if manager.find_indicator(name_):
                    return manager.candles

        return []

    def get_candles(self) -> Dict[str, List[Candle]]:
        return {name: manager.candles for name, manager in self._candle_map.items()}

    @property
    def settings(self) -> dict:
        output = {}

        for name, value in self.__dict__.items():
            if name in ["candles", "timeframe_fill"]:
                continue
            if name == "candlestick" and value:
                output[name] = value.acronym if value.acronym else value.name
            elif not name.startswith("_") and value is not None:
                output[name] = copy(value)

        output["candles"] = []

        if self._timeframe:
            output["timeframe"] = self.timeframe
            output["timeframe_fill"] = self.timeframe_fill

        output["indicators"] = self.indicator_settings

        for indicator in output["indicators"]:
            for k, v in output.items():
                if k in indicator and v == indicator[k]:
                    indicator.pop(k)

        return output

    @property
    def indicator_settings(self) -> List[dict]:
        """Simply get's a list of all the Indicators within Hexital strategy"""
        settings = []

        for indicator in self._indicators.values():
            conf = {}
            if isinstance(indicator, Indicator) and not isinstance(indicator, Amorph):
                conf.update(
                    {"indicator": indicator._name if indicator._name else type(indicator).__name__}
                )
            conf.update(indicator.settings)
            settings.append(conf)

        return settings

    def _find_indicator(self, source: Source) -> Indicator | None:
        if isinstance(source, Indicator):
            return source
        elif isinstance(source, NestedSource):
            return source.indicator
        elif indicator := self._indicators.get(source.split(".")[0]):
            return indicator

        return None

    def _find_reading(self, source: Source, index: int = -1) -> Reading:
        if isinstance(source, (Indicator, NestedSource)):
            return source.reading(index=index)
        elif reading := reading_by_index(
            self._candle_map[self._default_name].candles, source, index=index
        ):
            return reading

        for candle_manager in self._candle_map.values():
            reading = reading_by_index(candle_manager.candles, source, index=index)
            if reading is not None:
                return reading

        return None

    def _find_readings(self, source: Source) -> List[Reading]:
        if isinstance(source, (Indicator, NestedSource)):
            return source.readings()

        primary_name = source.split(".")[0]
        if self._indicators.get(primary_name):
            return self._indicators[primary_name].readings(source)

        return []

    def reading(self, source: Source, index: int = -1) -> Reading:
        """Attempts to retrieve a reading with a given Indicator name.
        `name` can use '.' to find nested reading, E.G `MACD_12_26_9.MACD`
        """
        return self._find_reading(source, index)

    def prev_reading(self, source: Source) -> Reading:
        return self._find_reading(source, -2)

    def readings(self) -> Dict[str, List[Reading]]:
        """Returns a Dictionary of all the Indicators and there results in a list format."""
        return {name: indicator.readings() for name, indicator in self._indicators.items()}

    def reading_as_list(self, source: Source) -> List[Reading]:
        """Find given indicator and returns the readings as a list
        Full Name of the indicator E.G `EMA_12` OR `MACD_12_26_9.MACD`"""
        return self._find_readings(source)

    def add_indicator(
        self, indicator: Indicator | List[Indicator | Dict[str, Any]] | Dict[str, Any]
    ):
        """Add's a new indicator to `Hexital` strategy.
        This accept either `Indicator` datatypes or dict string versions to be packed.
        `add_indicator(SMA(period=10))` or `add_indicator({"indicator": "SMA", "period": 10})`
        Does not automatically calculates readings."""
        indicators = indicator if isinstance(indicator, list) else [indicator]

        for name, valid_indicator in self._validate_indicators(indicators).items():
            self._indicators[name] = valid_indicator

    def remove_indicator(self, source: Source):
        """Removes an indicator from running within hexital"""
        indicator = self._find_indicator(source)
        if not indicator:
            return

        indicator.purge()
        self._indicators.pop(indicator.name)

    def prepend(
        self,
        candles: Candles,
        timeframe: Optional[TimeFramesSource] = None,
    ):
        """Prepends a Candle or a chronological ordered list of Candle's to the front of the Hexital Candle's. This will only re-sample and re-calculate the new Candles, with minor overlap.

        Args:
            candles: The Candle or List of Candle's to prepend.
            timeframe: A specific timeframe to insert Candle's into
        """
        timeframe_name = self._parse_timeframe(timeframe)

        if timeframe_name and self._candle_map.get(timeframe_name):
            self._candle_map[timeframe_name].prepend(candles)
        else:
            for candle_manager in self._candle_map.values():
                candle_manager.prepend(candles)

        self.calculate()

    def append(
        self,
        candles: Candles,
        timeframe: Optional[TimeFramesSource] = None,
    ):
        """append a Candle or a chronological ordered list of Candle's to the end of the Hexital Candle's. This wil only re-sample and re-calculate the new Candles, with minor overlap.

        Args:
            candles: The Candle or List of Candle's to prepend.
            timeframe: A specific timeframe to insert Candle's into
        """
        timeframe_name = self._parse_timeframe(timeframe)

        if timeframe_name and self._candle_map.get(timeframe_name):
            self._candle_map[timeframe_name].append(candles)
        else:
            for candle_manager in self._candle_map.values():
                candle_manager.append(candles)

        self.calculate()

    def insert(
        self,
        candles: Candles,
        timeframe: Optional[TimeFramesSource] = None,
    ):
        """insert a Candle or a list of Candle's to the Hexital Candles. This accepts any order or placement. This will sort, re-sample and re-calculate all Candles.

        Args:
            candles: The Candle or List of Candle's to prepend.
            timeframe: A specific timeframe to insert Candle's into
        """
        timeframe_name = self._parse_timeframe(timeframe)

        if timeframe_name and self._candle_map.get(timeframe_name):
            self._candle_map[timeframe_name].insert(candles)
        else:
            for candle_manager in self._candle_map.values():
                candle_manager.insert(candles)

        self.calculate_index(index=0, end_index=-1)

    def calculate(self, name: Optional[str] = None):
        """Calculates all the missing indicator readings."""
        for indicator_name, indicator in self._indicators.items():
            if name is None or indicator_name == name:
                indicator.calculate()

    def calculate_index(
        self, name: Optional[str] = None, index: int = -1, end_index: Optional[int] = None
    ):
        """Calculate specific index for all or specific indicator readings."""
        for indicator_name, indicator in self._indicators.items():
            if name is None or indicator_name == name:
                indicator.calculate_index(index, end_index)

    def recalculate(self, source: Optional[Source] = None):
        """Purge's all indicator reading's and re-calculates them all,
        ideal for changing an indicator parameters midway."""
        if not source:
            for indicator in self._indicators.values():
                indicator.purge()
                indicator.calculate()
        elif indicator := self._find_indicator(source):
            indicator.purge()
            indicator.calculate()

    def purge(self, source: Optional[Source] = None):
        """Takes Indicator name and removes all readings for said indicator.
        Indicator name must be exact"""
        if not source:
            for indicator in self._indicators.values():
                indicator.purge()
        elif indicator := self._find_indicator(source):
            indicator.purge()

    def _parse_timeframe(self, timeframe: Optional[TimeFramesSource]) -> str | None:
        if not timeframe:
            return None

        if timeframe == self._default_name:
            return self._default_name

        if not timeframe_validation(timeframe):
            return None

        name = convert_timeframe_to_timedelta(timeframe)

        return None if not name else timedelta_to_str(name)

    def _validate_indicators(self, indicators: Sequence[dict | Indicator]) -> Dict[str, Indicator]:
        if not indicators:
            return {}

        valid_indicators: Dict[str, Indicator] = {}

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
            if indicator.candle_manager.name in self._candle_map:
                indicator.candle_manager = self._candle_map[indicator.candle_manager.name]
            elif indicator.candle_manager.name == DEFAULT_CANDLES:
                indicator.candle_manager = self._candle_map[self._default_name]
            else:
                manager = CandleManager(
                    [],
                    candle_life=self.candle_life,
                    timeframe=indicator._timeframe if indicator._timeframe else self._timeframe,
                    timeframe_fill=self.timeframe_fill,
                    candlestick=indicator.candlestick
                    if indicator.candlestick
                    else self.candlestick,
                )

                manager.append(self._candle_map[self._default_name].candles)
                self._candle_map[manager.name] = manager
                indicator.candle_manager = manager

        return valid_indicators

    def _build_indicator(self, raw_indicator: dict) -> Indicator:
        indicator = copy(raw_indicator)

        if indicator.get("indicator"):
            indicator_name = indicator.pop("indicator")
            indicator_class = getattr(import_module("hexital.indicators"), indicator_name, None)

            if indicator_class:
                return indicator_class(**indicator)
            else:
                raise InvalidIndicator(
                    f"Indicator {indicator_name} does not exist. [{raw_indicator}]"
                )

        elif indicator.get("analysis") and isinstance(indicator.get("analysis"), str):
            analysis_name = indicator.pop("analysis")
            analysis_class = getattr(import_module("hexital.analysis"), analysis_name, None)

            if not analysis_class:
                raise InvalidAnalysis(
                    f"analysis {analysis_name} does not exist in patterns or movements. [{raw_indicator}]"
                )

            return Amorph(analysis=analysis_class, **indicator)

        elif indicator.get("analysis") and callable(indicator.get("analysis")):
            method_name = indicator.pop("analysis")
            return Amorph(analysis=method_name, **indicator)
        else:
            raise InvalidAnalysis(
                f"Dict Indicator missing 'indicator' or 'analysis' name, not: {raw_indicator}"
            )

    def find_candle_pairing(
        self, indicator: str, indicator_cmp: Optional[str] = None
    ) -> Tuple[List[Candle], List[Candle]]:
        reverted = False

        if indicator and not indicator_cmp:
            return self.candles(indicator), []

        if indicator_cmp and indicator in ["open", "high", "low", "close", "volume"]:
            indicator, indicator_cmp = indicator_cmp, indicator
            reverted = True

        candles = self.candles(indicator)

        if candles and indicator_cmp and reading_by_candle(candles[-1], indicator_cmp) is not None:
            return candles, candles
        elif candles and indicator_cmp and reading_by_candle(candles[-1], indicator_cmp) is None:
            if reverted:
                return self.candles(indicator_cmp), candles
            else:
                return candles, self.candles(indicator_cmp)

        return [], []


T = TypeVar("T", bound=IndicatorCollection)


class HexitalCol(Generic[T], Hexital):
    collection: T

    def __init__(
        self,
        name: str,
        candles: List[Candle],
        indicators: T,
        description: Optional[str] = None,
        timeframe: Optional[TimeFramesSource] = None,
        timeframe_fill: bool = False,
        candle_life: Optional[timedelta] = None,
        candlestick: Optional[CandlestickType | str] = None,
    ):
        self.collection = indicators

        super().__init__(
            name,
            candles,
            indicators.collection_list(),
            description,
            timeframe,
            timeframe_fill,
            candle_life,
            candlestick,
        )
