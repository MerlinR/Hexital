from copy import copy
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
from hexital.utils.candles import reading_by_candle, reading_by_index
from hexital.utils.candlesticks import validate_candlesticktype
from hexital.utils.timeframe import (
    TimeFrame,
    convert_timeframe_to_timedelta,
    timedelta_to_str,
    timeframe_validation,
)


class Hexital:
    name: str
    _candles: Dict[str, CandleManager]
    _indicators: Dict[str, Indicator]
    description: Optional[str] = None
    _timeframe: Optional[timedelta] = None
    _timeframe_name: str = DEFAULT_CANDLES
    timeframe_fill: bool = False
    candle_life: Optional[timedelta] = None
    candlestick: Optional[CandlestickType] = None

    def __init__(
        self,
        name: str,
        candles: List[Candle],
        indicators: Optional[List[dict | Indicator]] = None,
        description: Optional[str] = None,
        timeframe: Optional[str | TimeFrame | timedelta | int] = None,
        timeframe_fill: bool = False,
        candle_life: Optional[timedelta] = None,
        candlestick: Optional[CandlestickType | str] = None,
    ):
        self.name = name
        self.description = description

        self._timeframe = convert_timeframe_to_timedelta(timeframe)
        self.timeframe_fill = timeframe_fill
        self.candle_life = candle_life

        if candlestick:
            self.candlestick = validate_candlesticktype(candlestick)

        if self._timeframe:
            self._timeframe_name = timedelta_to_str(self._timeframe)

        self._candles = {
            self._timeframe_name: CandleManager(
                candles if isinstance(candles, list) else [],
                candle_life=self.candle_life,
                timeframe=self._timeframe,
                timeframe_fill=self.timeframe_fill,
                candlestick=self.candlestick,
            )
        }

        self._indicators = self._validate_indicators(indicators) if indicators else {}

    @property
    def timeframe(self) -> str | None:
        return self._timeframe_name if self._timeframe else None

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

    def has_reading(self, name: str) -> bool:
        """Checks if the given Indicator has a valid reading in latest Candle"""
        value = self.reading(name)
        if isinstance(value, dict):
            return any(v is not None for v in value.values())
        return value is not None

    def candles(self, name: Optional[str | TimeFrame | timedelta | int] = None) -> List[Candle]:
        """Get a set of candles by using either a Timeframe or Indicator name"""
        name_ = name if name else self._timeframe_name
        timeframe_name = self._parse_timeframe(name)

        name_ = timeframe_name if timeframe_name else name_

        if isinstance(name_, str) and self._candles.get(name_, False):
            return self._candles[name_].candles
        elif isinstance(name_, str):
            for manager in self._candles.values():
                if manager.find_indicator(name_):
                    return manager.candles

        return []

    def get_candles(self) -> Dict[str, List[Candle]]:
        return {name: manager.candles for name, manager in self._candles.items()}

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

    def reading(self, name: str, index: int = -1) -> float | dict | None:
        """Attempts to retrieve a reading with a given Indicator name.
        `name` can use '.' to find nested reading, E.G `MACD_12_26_9.MACD`
        """
        reading = reading_by_index(self._candles[self._timeframe_name].candles, name, index=index)

        if reading is not None:
            return reading

        for candle_manager in self._candles.values():
            reading = reading_by_index(candle_manager.candles, name, index=index)
            if reading is not None:
                return reading

        return None

    def prev_reading(self, name: str) -> float | dict | None:
        return self.reading(name, index=-2)

    def readings(self) -> Dict[str, List[float | dict | None]]:
        """Returns a Dictionary of all the Indicators and there results in a list format."""

        return {name: indicator.as_list() for name, indicator in self._indicators.items()}

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

    def append(
        self,
        candles: Candle | List[Candle] | dict | List[dict] | list | List[list],
        timeframe: Optional[str | TimeFrame | timedelta | int] = None,
    ):
        timeframe_name = self._parse_timeframe(timeframe)

        if timeframe_name and self._candles.get(timeframe_name):
            self._candles[timeframe_name].append(candles)
        else:
            for candle_manager in self._candles.values():
                candle_manager.append(candles)

        self.calculate()

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

    def purge(self, name: Optional[str] = None):
        """Takes Indicator name and removes all readings for said indicator.
        Indicator name must be exact"""
        for indicator_name, indicator in self._indicators.items():
            if name is None or (name and name in indicator_name):
                indicator.purge()

    def _parse_timeframe(
        self, timeframe: Optional[str | TimeFrame | timedelta | int]
    ) -> str | None:
        if not timeframe:
            return None

        if timeframe == self._timeframe_name:
            return self._timeframe_name

        if not timeframe_validation(timeframe):
            return None

        name = convert_timeframe_to_timedelta(timeframe)

        return None if not name else timedelta_to_str(name)

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
                indicator.candle_manager = self._candles[self._timeframe_name]
            elif indicator.timeframe and indicator.timeframe in self._candles:
                indicator.candle_manager = self._candles[indicator.timeframe]
            else:
                manager = CandleManager(
                    [],
                    candle_life=self.candle_life,
                    timeframe=indicator._timeframe if indicator._timeframe else self._timeframe,
                    timeframe_fill=self.timeframe_fill,
                    candlestick=self.candlestick,
                )
                manager.append(self._candles[self._timeframe_name].candles)
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

    def find_candles(
        self, indicator: str, indicator_cmp: Optional[str] = None
    ) -> List[List[Candle]]:
        reverted = False

        if indicator and not indicator_cmp:
            return [self.candles(indicator), []]

        if indicator_cmp and indicator in ["open", "high", "low", "close", "volume"]:
            indicator, indicator_cmp = indicator_cmp, indicator
            reverted = True

        candles = self.candles(indicator)

        if candles and indicator_cmp and reading_by_candle(candles[-1], indicator_cmp) is not None:
            return [candles, candles]
        elif candles and indicator_cmp and reading_by_candle(candles[-1], indicator_cmp) is None:
            if reverted:
                return [self.candles(indicator_cmp), candles]
            else:
                return [candles, self.candles(indicator_cmp)]

        return [[]]
