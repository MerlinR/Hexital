from __future__ import annotations

from abc import ABC, abstractmethod
from copy import copy
from dataclasses import dataclass, field
from datetime import timedelta
from enum import Enum, auto
from typing import Dict, Generic, List, Optional, Tuple, TypeAlias, TypeVar

from hexital.core import Reading
from hexital.core.candle import Candle
from hexital.core.candle_manager import CandleManager, Candles
from hexital.core.candlestick_type import CandlestickType
from hexital.utils.candles import (
    candles_average,
    candles_sum,
    get_readings_period,
    reading_by_candle,
    reading_by_index,
    reading_count,
    reading_period,
)
from hexital.utils.candlesticks import validate_candlesticktype
from hexital.utils.common import round_values
from hexital.utils.indexing import absindex, valid_index
from hexital.utils.timeframe import (
    TimeFramesSource,
    convert_timeframe_to_timedelta,
    timedelta_to_str,
)

T = TypeVar("T")
V = TypeVar("V")


class IndicatorMode(Enum):
    SOLO = auto()
    SUB = auto()
    MANAGED = auto()


@dataclass(kw_only=True)
class Indicator(Generic[V], ABC):
    candles: List[Candle] = field(default_factory=list)
    name: str = ""
    timeframe: Optional[TimeFramesSource] = None
    timeframe_fill: bool = False
    candle_life: Optional[timedelta] = None
    candlestick: Optional[CandlestickType | str] = None
    rounding: Optional[int] = 4

    sub_indicators: Dict[str, Indicator] = field(init=False, default_factory=dict)
    managed_indicators: Dict[str, Managed | Indicator] = field(init=False, default_factory=dict)
    _mode: IndicatorMode = field(init=False, default=IndicatorMode.SOLO)
    _generated_name: bool = field(init=False, default=False)
    _calc_prior: bool = field(init=False, default=True)
    _active_index: int = field(init=False, default=0)

    _name: str = field(init=False, default="")
    _timeframe: Optional[timedelta] = field(init=False)
    _candle_mngr: CandleManager = field(init=False)

    _initialised: bool = field(init=False, default=False)

    def __post_init__(self):
        self._validate_fields()

        self._timeframe = convert_timeframe_to_timedelta(self.timeframe)
        self.timeframe = timedelta_to_str(self._timeframe) if self._timeframe else None

        if self.candlestick is not None:
            self.candlestick = validate_candlesticktype(self.candlestick)

        self._candle_mngr = CandleManager(
            self.candles,
            self.candle_life,
            self._timeframe,
            self.timeframe_fill,
            self.candlestick,
        )

        self.candles = self._candle_mngr.candles

        self._internal_generate_name()

    def __repr__(self) -> str:
        return self.name

    def _internal_generate_name(self):
        if self.name:
            name = self.name
        else:
            self._generated_name = True
            name = self._generate_name()
            if self._candle_mngr.timeframe:
                name += f"_{self._candle_mngr.name}"

        self.name = name.replace(".", "-")

    def _initialise(self):
        return

    def _validate_fields(self):
        return

    @abstractmethod
    def _generate_name(self) -> str: ...

    @property
    def candle_manager(self) -> CandleManager:
        """The Candle Manager which controls TimeFrame, Trimming and collapsing"""
        return self._candle_mngr

    @candle_manager.setter
    def candle_manager(self, manager: CandleManager):
        """The Candle Manager which controls TimeFrame, Trimming and collapsing,
        this will overwrite the Manager as well as the candles"""
        self._candle_mngr = manager
        self.candles = manager.candles
        self.timeframe = timedelta_to_str(manager.timeframe) if manager.timeframe else None
        self._timeframe = manager.timeframe
        self.timeframe_fill = manager.timeframe_fill
        self.candle_life = manager.candle_life
        self.candlestick = manager.candlestick

    @property
    def settings(self) -> dict:
        """
        Retrieve the settings required to regenerate this indicator in a dictionary format.

        This property compiles the configuration details of the indicator, excluding attributes
        that are irrelevant for generation (e.g., candles and sub-indicators). It ensures the
        output dictionary is clean and contains only the necessary settings for recreating the
        indicator.

        Special handling is included for attributes like `candlestick` and `timeframe`, ensuring
        their values are properly formatted.

        Returns:
            dict: A dictionary containing the indicator's settings, ready for regeneration.
                - `indicator` (str): The name of the indicator.
                - Additional keys correspond to other configuration attributes of the indicator.
        """
        output = {}

        for name, value in self.__dict__.items():
            if name in ["candles", "managed_indicators", "sub_indicators"]:
                continue
            if name == "timeframe_fill" and self._timeframe is None:
                continue

            if name == "candlestick" and value:
                output[name] = value.acronym if value.acronym else value.name
            elif name == "timeframe" and self._candle_mngr.timeframe is not None:
                output[name] = timedelta_to_str(self._candle_mngr.timeframe)
            elif not name.startswith("_") and value is not None:
                output[name] = copy(value)

        return output

    def readings(self, name: Optional[Source] = None) -> List[Reading | V]:
        """
        Retrieve the indicator readings for within the candles as a list.

        This method collects the readings of a specified indicator for all candles
        and returns them as a list. If no name is provided, the generated name of
        the indicator is used.

        Args:
            name (Optional[str]): The name of the indicator to retrieve.
                                  Defaults to `self.name` if not provided.

        Returns:
            List[float | dict | None]: A list containing the indicator values for
                                       each candle. The values may be floats,
                                       dictionaries (for complex indicators),
                                       or `None` if no reading is available.
        """
        return self._find_readings(name)

    def prepend(self, candles: Candles):
        """Prepends a Candle or a chronological ordered list of Candle's to the front of the Indicator Candle's. This will only re-sample and re-calculate the new Candles, with minor overlap.

        Args:
            candles: The Candle or List of Candle's to prepend.
        """

        self._candle_mngr.prepend(candles)
        self.calculate()

    def append(self, candles: Candles):
        """append a Candle or a chronological ordered list of Candle's to the end of the Indicator Candle's. This wil only re-sample and re-calculate the new Candles, with minor overlap.

        Args:
            candles: The Candle or List of Candle's to prepend.
        """
        self._candle_mngr.append(candles)
        self.calculate()

    def insert(self, candles: Candles):
        """insert a Candle or a list of Candle's to the Indicator Candles. This accepts any order or placement. This will sort, re-sample and re-calculate all Candles.

        Args:
            candles: The Candle or List of Candle's to prepend.
        """
        self._candle_mngr.insert(candles)
        self.calculate_index(0, -1)

    @property
    def prior_calc(self) -> bool:
        if self._mode != IndicatorMode.SOLO and self._calc_prior:
            return True
        return False

    @abstractmethod
    def _calculate_reading(self, index: int) -> V: ...

    def _calculate_sub_indicators(
        self,
        prior_calc: bool,
        index: int,
        end_index: Optional[int] = None,
    ):
        for indicator in self.sub_indicators.values():
            if indicator.prior_calc == prior_calc:
                indicator.calculate_index(index, end_index)

    def check_initialised(self):
        if not self._initialised:
            self._initialise()
            self._initialised = True

    def calculate(self):
        """Calculate the TA values, will calculate for all the Candles,
        where this indicator is missing"""
        self.check_initialised()

        for index in range(self._find_calc_index(), len(self.candles)):
            self._set_active_index(index)
            self._calculate_sub_indicators(True, index)

            reading = round_values(self._calculate_reading(index=index), round_by=self.rounding)

            if index < len(self.candles) - 1 and self._reading_dup(reading, self.candles[index]):
                break

            self._set_reading(reading, index)
            self._calculate_sub_indicators(False, index)

    def _reading_dup(self, reading: Reading | V, candle: Candle) -> bool:
        """Optimisation method for 'calculate'.
        if calculating and not on latest Candle, check if reading match's a pre-existing reading.
        This prevent's it from continuing calculating if already has readings
        It also means if Candles are prepended they will be calculated, and already calculated readings
        will be re-calculated using new prepended candles data until the reading stabilises.
        """
        if reading is None:
            return False
        cur_reading = candle.indicators.get(self.name, candle.sub_indicators.get(self.name))

        if cur_reading is None:
            return False

        elif reading == cur_reading:
            return True
        return False

    def calculate_index(self, start_index: int, end_index: Optional[int] = None):
        """Calculate the TA values, will calculate a index range the Candles, will re-calculate"""
        self.check_initialised()

        start_index = absindex(start_index, len(self.candles))

        if end_index is not None:
            end_index = absindex(end_index, len(self.candles))
        else:
            end_index = start_index

        for index in range(start_index, end_index + 1):
            self._set_active_index(index)
            self._calculate_sub_indicators(True, index)

            reading = round_values(self._calculate_reading(index=index), self.rounding)

            self._set_reading(reading, index)
            self._calculate_sub_indicators(False, index)

    def _find_calc_index(self) -> int:
        """Optimisation method, to find where to start calculating the indicator from
        Searches from newest to oldest to find the first candle without the indicator
        """
        if not self.candles or (
            self.name not in self.candles[0].indicators
            and self.name not in self.candles[0].sub_indicators
        ):
            return 0

        for index in range(len(self.candles) - 1, -1, -1):
            if (
                self.name in self.candles[index].indicators
                or self.name in self.candles[index].sub_indicators
            ):
                return index + 1

        return 0

    def _set_reading(self, reading: Reading, index: Optional[int] = None):
        index = index if index else self._active_index

        if self._mode != IndicatorMode.SOLO:
            self.candles[index].sub_indicators[self.name] = reading
        else:
            self.candles[index].indicators[self.name] = reading

    def _set_active_index(self, index: int):
        self._active_index = index
        for indicator in self.managed_indicators.values():
            if isinstance(indicator, Managed):
                indicator.set_active_index(index)

    def add_sub_indicator(self, indicator: Indicator, prior_calc: bool = True) -> Indicator:
        """Adds sub indicator, this will auto calculate with indicator"""
        indicator._mode = IndicatorMode.SUB
        indicator._calc_prior = prior_calc

        if indicator._generated_name:
            indicator.name = f"{self.name}-{indicator.name}"

        indicator.candle_manager = self._candle_mngr
        indicator.rounding = None
        self.sub_indicators[indicator.name] = indicator
        return self.sub_indicators[indicator.name]

    def add_managed_indicator(self, indicator: N) -> N:
        """Adds managed sub indicator, this will not auto calculate with indicator"""
        indicator._mode = IndicatorMode.MANAGED

        if indicator.name == MANAGED_NAME:
            indicator.name = f"{self.name}_data"
        elif indicator._generated_name:
            indicator.name = f"{self.name}-{indicator.name}"

        indicator.candle_manager = self._candle_mngr
        indicator.rounding = None
        self.managed_indicators[indicator.name] = indicator
        return indicator

    def _find_reading(
        self, source: Optional[Source] = None, index: Optional[int] = None
    ) -> Reading | V:
        if index is None:
            index = self._active_index
        elif valid_index(index, len(self.candles)):
            index = index
        else:
            return None

        if not source or (isinstance(source, str) and source == self.name):
            return reading_by_index(self.candles, self.name, index)
        elif isinstance(source, str):
            return reading_by_index(self.candles, source, index)
        else:
            return reading_by_index(self.candles, source.name, index)

    def _find_readings(self, source: Optional[Source] = None) -> List[Reading | V]:
        if not source:
            return [reading_by_candle(candle, self.name) for candle in self.candles]
        elif isinstance(source, Indicator):
            return [reading_by_candle(candle, source.name) for candle in self.candles]
        elif isinstance(source, NestedSource):
            return source.readings()
        elif isinstance(source, str):
            return [reading_by_candle(candle, source) for candle in self.candles]

    def _find_candles(self, source: Optional[Source] = None) -> Tuple[List[Candle], str]:
        if not source or (isinstance(source, str) and source == self.name):
            return self.candles, self.name
        elif isinstance(source, str):
            return self.candles, source
        else:
            return source.candles, source.name

    def exists(self, source: Optional[Source] = None) -> bool:
        value = self._find_reading(source)
        if isinstance(value, dict):
            return any(v is not None for v in value.values())
        return value is not None

    def prev_exists(self, source: Optional[Source] = None) -> bool:
        if self._active_index == 0:
            return False
        value = self._find_reading(source, self._active_index - 1)
        if isinstance(value, dict):
            return any(v is not None for v in value.values())
        return value is not None

    def prev_reading(
        self, source: Optional[Source] = None, default: Optional[T] = None
    ) -> Reading | V | T:
        if self._active_index == 0:
            return default
        value = self._find_reading(source, self._active_index - 1)
        return value if value is not None else default

    def reading(
        self,
        source: Optional[Source] = None,
        index: Optional[int] = None,
        default: Optional[T] = None,
    ) -> Reading | V | T:
        """Simple method to get an indicator reading from the index"""
        value = self._find_reading(source, index)
        return value if value is not None else default

    def reading_count(self, source: Optional[Source] = None, index: Optional[int] = None) -> int:
        """Returns how many instance of the given indicator exist"""
        return reading_count(
            *self._find_candles(source),
            index if index is not None else self._active_index,
        )

    def reading_period(
        self, period: int, source: Optional[Source] = None, index: Optional[int] = None
    ) -> bool:
        """Will return True if the given indicator goes back as far as amount,
        It's true if exactly or more than. Period will be period -1"""
        return reading_period(
            *self._find_candles(source),
            period,
            index if index is not None else self._active_index,
        )

    def candles_sum(
        self,
        length: int = 1,
        source: Optional[Source] = None,
        index: Optional[int] = None,
        include_latest: bool = True,
    ) -> float:
        return candles_sum(
            *self._find_candles(source),
            length,
            index if index is not None else self._active_index,
            include_latest,
        )

    def candles_average(
        self,
        length: int = 1,
        source: Optional[Source] = None,
        index: Optional[int] = None,
        include_latest: bool = True,
    ) -> float:
        return candles_average(
            *self._find_candles(source),
            length,
            index if index is not None else self._active_index,
            include_latest,
        )

    def get_readings_period(
        self,
        length: int = 1,
        source: Optional[Source] = None,
        index: Optional[int] = None,
        include_latest: bool = False,
    ) -> List[float | int]:
        return get_readings_period(
            *self._find_candles(source),
            length,
            index if index is not None else self._active_index,
            include_latest,
        )

    def purge(self):
        """Remove this indicator value from all Candles"""
        self._candle_mngr.purge(
            {self.name}
            | {indicator.name for indicator in self.sub_indicators.values()}
            | {indicator.name for indicator in self.managed_indicators.values()}
        )

    def recalculate(self):
        """Re-calculate this indicator value for all Candles"""
        self.purge()
        self.calculate()


MANAGED_NAME = "MAN"


@dataclass(kw_only=True)
class Managed(Indicator):
    """Managed

    Empty Indicator thats manually controlled and the reading manually set.

    """

    _name: str = field(init=False, default=MANAGED_NAME)
    _mode: IndicatorMode = field(init=False, default=IndicatorMode.MANAGED)
    _active_index: int = field(default=0)

    def _generate_name(self) -> str:
        return self._name

    def _calculate_reading(self, index: int) -> Reading: ...

    def set_reading(self, reading: Reading, index: Optional[int] = None):
        if index is None:
            index = self._active_index
        else:
            self.set_active_index(index)

        self._calculate_sub_indicators(True, index)
        self._set_reading(reading, index)
        self._calculate_sub_indicators(False, index)

    def set_active_index(self, index: int):
        self._active_index = index


class NestedSource:
    indicator: Indicator
    nested_name: str

    def __init__(self, indicator: Indicator, nested_name: str):
        self.indicator = indicator
        self.nested_name = nested_name

    @property
    def candles(self):
        return self.indicator.candles

    @property
    def name(self):
        return f"{self.indicator.name}.{self.nested_name}"

    def reading(self, index: Optional[int] = None) -> Reading:
        value = self.indicator.reading(index=index)
        if isinstance(value, dict):
            return value.get(self.nested_name)
        return value

    def readings(self) -> List[Reading]:
        return [
            v.get(self.nested_name) if isinstance(v, dict) else v
            for v in self.indicator.readings()
        ]

    def __str__(self):
        return f"{self.indicator.name}.{self.nested_name}"


Source: TypeAlias = str | Indicator | NestedSource
N = TypeVar("N", Indicator, Managed)
