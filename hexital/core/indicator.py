from __future__ import annotations

from abc import ABC, abstractmethod
from copy import copy
from dataclasses import dataclass, field
from datetime import timedelta
from typing import Dict, List, Optional, TypeAlias, TypeVar

from hexital.core.candle import Candle
from hexital.core.candle_manager import CandleManager
from hexital.core.candlestick_type import CandlestickType
from hexital.core.types import (
    Candles,
    NullReading,
    NullReadingType,
    Reading,
    is_none,
    is_null_conv,
)
from hexital.utils.candles import (
    candles_average,
    candles_sum,
    get_readings_period,
    reading_count,
    reading_period,
)
from hexital.utils.candlesticks import validate_candlesticktype
from hexital.utils.indexing import absindex, round_values, valid_index
from hexital.utils.timeframe import TimeFrame, convert_timeframe_to_timedelta, timedelta_to_str

T = TypeVar("T")


@dataclass(kw_only=True)
class Indicator(ABC):
    candles: List[Candle] = field(default_factory=list)
    name: str = ""
    timeframe: Optional[str | TimeFrame | timedelta | int] = None
    timeframe_fill: bool = False
    candle_life: Optional[timedelta] = None
    candlestick: Optional[CandlestickType | str] = None
    rounding: Optional[int] = 4

    sub_indicators: Dict[str, Indicator] = field(init=False, default_factory=dict)
    managed_indicators: Dict[str, Managed | Indicator] = field(init=False, default_factory=dict)
    _sub_indicator: bool = field(init=False, default=False)
    _sub_calc_prior: bool = field(init=False, default=True)

    _name: str = field(init=False, default="")
    _readings: list = field(init=False, default_factory=list)
    _timeframe: Optional[timedelta] = field(init=False)
    _candles: CandleManager = field(init=False)
    _active_index: int = field(init=False, default=0)
    _initialised: bool = field(init=False, default=False)

    def __post_init__(self):
        self._validate_fields()

        self._timeframe = convert_timeframe_to_timedelta(self.timeframe)
        self.timeframe = timedelta_to_str(self._timeframe) if self._timeframe else None

        if self.candlestick is not None:
            self.candlestick = validate_candlesticktype(self.candlestick)

        self._candles = CandleManager(
            self.candles,
            self.candle_life,
            self._timeframe,
            self.timeframe_fill,
            self.candlestick,
        )

        self.candles = self._candles.candles
        self.sync_readings(len(self.candles))

        self._internal_generate_name()

    def __str__(self):
        return self.name

    def _internal_generate_name(self):
        name = ""

        if self.name:
            name = self.name
        else:
            name = self._generate_name()
            if self._candles.timeframe:
                name += f"_{self._candles.name}"

        self.name = self._sanitise_name(name)

    def _initialise(self):
        return

    def _validate_fields(self):
        return

    @abstractmethod
    def _generate_name(self) -> str: ...

    def _sanitise_name(self, name: str) -> str:
        return name.replace(".", ",")

    @property
    def candle_manager(self) -> CandleManager:
        """The Candle Manager which controls TimeFrame, Trimming and collapsing"""
        return self._candles

    @candle_manager.setter
    def candle_manager(self, manager: CandleManager):
        """The Candle Manager which controls TimeFrame, Trimming and collapsing,
        this will overwrite the Manager as well as the candles"""
        self._candles = manager
        self.candles = manager.candles
        self.sync_readings(len(self.candles))
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
            elif name == "timeframe" and self._candles.timeframe is not None:
                output[name] = timedelta_to_str(self._candles.timeframe)
            elif not name.startswith("_") and value is not None:
                output[name] = copy(value)

        return output

    @property
    def readings(self) -> List[Reading]:
        return [is_null_conv(v) for v in self._readings]

    def prepend(self, candles: Candles):
        """Prepends a Candle or a chronological ordered list of Candle's to the front of the Indicator Candle's. This will only re-sample and re-calculate the new Candles, with minor overlap.

        Args:
            candles: The Candle or List of Candle's to prepend.
        """

        self._candles.prepend(candles)
        self.sync_readings(prepend=True)
        self.calculate()

    def append(self, candles: Candles):
        """append a Candle or a chronological ordered list of Candle's to the end of the Indicator Candle's. This wil only re-sample and re-calculate the new Candles, with minor overlap.

        Args:
            candles: The Candle or List of Candle's to prepend.
        """
        self._candles.append(candles)
        self.sync_readings()
        self.calculate()

    def insert(self, candles: Candles):
        """insert a Candle or a list of Candle's to the Indicator Candles. This accepts any order or placement. This will sort, re-sample and re-calculate all Candles.

        Args:
            candles: The Candle or List of Candle's to prepend.
        """
        self._candles.insert(candles)
        self.sync_readings()
        self.calculate_index(0, -1)

    def sync_readings(self, length: Optional[int] = None, prepend: bool = False):
        length = length if length else abs(len(self._readings) - len(self.candles))

        if not length:
            return

        for _ in range(length):
            if prepend:
                self._readings.insert(0, NullReading)
            else:
                self._readings.append(NullReading)

        for indicator in self.sub_indicators.values():
            indicator.sync_readings(length, prepend)
        for indicator in self.managed_indicators.values():
            indicator.sync_readings(length, prepend)

    @property
    def prior_calc(self) -> bool:
        if self._sub_indicator and self._sub_calc_prior:
            return True
        return False

    @abstractmethod
    def _calculate_reading(self, index: int) -> Reading: ...

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

            if index < len(self._readings) - 1 and self._reading_dup(reading, index):
                break

            self._set_reading(reading, index)
            self._calculate_sub_indicators(False, index)

    def _reading_dup(self, reading: Reading | None, index: int) -> bool:
        """Optimisation method for 'calculate'.
        if calculating and not on latest Candle, check if reading match's a pre-existing reading.
        This prevent's it from continuing calculating if already has readings
        It also means if Candles are prepended they will be calculated, and already calculated readings
        will be re-calculated using new prepended candles data until the reading stabilises.
        """
        if reading is None:
            return False

        cur_reading = self._readings[index]

        if cur_reading is NullReading:
            return False
        elif isinstance(cur_reading, dict) and isinstance(reading, dict):
            # TODO find a good way to detect if dict is same or not
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
        if not self.candles or self._readings[0] is NullReading:
            return 0

        for index in range(len(self._readings) - 1, -1, -1):
            if not is_none(self._readings[index]):
                return index + 1

        return 0

    def _set_reading(self, reading: Reading, index: Optional[int] = None):
        index = index if index else self._active_index
        self._readings[index] = reading

    def _set_active_index(self, index: int):
        self._active_index = index
        for indicator in self.managed_indicators.values():
            if isinstance(indicator, Managed):
                indicator.set_active_index(index)

    def add_sub_indicator(self, indicator: Indicator, prior_calc: bool = True) -> Indicator:
        """Adds sub indicator, this will auto calculate with indicator"""
        indicator._sub_indicator = True
        indicator._sub_calc_prior = prior_calc
        indicator.candle_manager = self._candles
        indicator.rounding = None
        self.sub_indicators[indicator.name] = indicator
        return self.sub_indicators[indicator.name]

    def add_managed_indicator(self, indicator: Managed | Indicator) -> Managed | Indicator:
        """Adds managed sub indicator, this will not auto calculate with indicator"""
        if indicator.name == MANAGED_NAME:
            indicator.name = f"{self.name}_data"
        indicator._sub_indicator = True
        indicator.candle_manager = self._candles
        indicator.rounding = None
        self.managed_indicators[indicator.name] = indicator
        return self.managed_indicators[indicator.name]

    def _find_reading(
        self, source: Source | None = None, index: Optional[int] = None
    ) -> Reading | NullReadingType:
        if not source or (isinstance(source, str) and source == self.name):
            if not self._readings or (
                index is not None and not valid_index(index, len(self._readings))
            ):
                return None
            return self._readings[self._active_index] if index is None else self._readings[index]
        elif isinstance(source, str) and self.sub_indicators.get(source):
            return self.sub_indicators[source].reading(index=index)
        elif isinstance(source, str):
            if not self.candles or (
                index is not None and not valid_index(index, len(self.candles))
            ):
                return None
            return getattr(
                self.candles[self._active_index if index is None else index], source, None
            )
        elif isinstance(source, Indicator):
            return source.reading(index=index)
        elif isinstance(source, NestedSource):
            return source.reading(index)

    def _find_readings(self, source: Source | None = None) -> List[Reading | NullReadingType]:
        if not source or (isinstance(source, str) and source == self.name):
            return self._readings
        elif isinstance(source, str) and self.sub_indicators.get(source):
            return self.sub_indicators[source]._find_readings()
        elif isinstance(source, str) and self.candles and getattr(self.candles[0], source, None):
            return [getattr(v, source) for v in self.candles]
        elif isinstance(source, Indicator):
            return source._readings
        elif isinstance(source, NestedSource):
            return source._readings
        return []

    def exists(self, source: Optional[Source] = None) -> bool:
        value = self._find_reading(source)
        if isinstance(value, dict):
            return any(not is_none(v) for v in value.values())
        return not is_none(value)

    def prev_exists(self, source: Optional[Source] = None) -> bool:
        if self._active_index == 0:
            return False
        value = self._find_reading(source, self._active_index - 1)
        if isinstance(value, dict):
            return any(not is_none(v) for v in value.values())
        return not is_none(value)

    def prev_reading(
        self, source: Optional[Source] = None, default: Optional[T] = None
    ) -> Reading | T:
        if self._active_index == 0:
            return default
        value = self._find_reading(source, self._active_index - 1)
        return value if not is_none(value) else default

    def reading(
        self,
        source: Source | None = None,
        index: Optional[int] = None,
        default: Optional[T] = None,
    ) -> Reading | T:
        """Simple method to get an indicator reading from the index
        Name can use '.' to find nested reading, E.G 'MACD_12_26_9.MACD"""
        value = self._find_reading(source, index)
        return value if not is_none(value) else default

    def reading_count(self, source: Source | None = None, index: Optional[int] = None) -> int:
        """Returns how many instance of the given indicator exist"""
        return reading_count(
            self._find_readings(source),
            index if index is not None else self._active_index,
        )

    def reading_period(
        self, period: int, source: Source | None = None, index: Optional[int] = None
    ) -> bool:
        """Will return True if the given indicator goes back as far as amount,
        It's true if exactly or more than. Period will be period -1"""

        return reading_period(
            self._find_readings(source),
            period,
            index if index is not None else self._active_index,
        )

    def candles_sum(
        self,
        length: int = 1,
        source: Source | None = None,
        index: Optional[int] = None,
        include_latest: bool = True,
    ) -> float | None:
        return candles_sum(
            self._find_readings(source),
            length,
            index if index is not None else self._active_index,
            include_latest,
        )

    def candles_average(
        self,
        length: int = 1,
        source: Source | None = None,
        index: Optional[int] = None,
        include_latest: bool = True,
    ) -> float | None:
        return candles_average(
            self._find_readings(source),
            length,
            index if index is not None else self._active_index,
            include_latest,
        )

    def get_readings_period(
        self,
        length: int = 1,
        source: Source | None = None,
        index: Optional[int] = None,
        include_latest: bool = False,
    ) -> List[float | int]:
        return get_readings_period(
            self._find_readings(source),
            length,
            index if index is not None else self._active_index,
            include_latest,
        )

    def purge(self):
        """Remove this indicator value from all Candles"""
        self._candles.purge(
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
    _sub_indicator: bool = field(default=True)
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

    def reading(self, index: Optional[int] = None) -> Reading:
        value = self.indicator.reading(index=index)
        if isinstance(value, dict):
            return value.get(self.nested_name)
        return value

    @property
    def _readings(self) -> List[Reading | NullReadingType]:
        return [v.get(self.nested_name) for v in self.indicator.readings if isinstance(v, dict)]

    @property
    def readings(self) -> List[Reading]:
        return [
            v.get(self.nested_name) if isinstance(v, dict) else is_null_conv(v)
            for v in self.indicator.readings
        ]

    @property
    def timeframe(self) -> timedelta | None:
        return self.indicator._timeframe

    def __str__(self):
        return f"{self.indicator.name}.{self.nested_name}"


Source: TypeAlias = str | Indicator | NestedSource
