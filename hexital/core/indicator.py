from __future__ import annotations

from abc import ABC, abstractmethod
from copy import copy
from dataclasses import dataclass, field
from datetime import timedelta
from enum import Enum
from typing import Generic, TypeAlias, TypeVar

from ..exceptions import InvalidIndicator
from ..utils.candles import (
    Candles,
    candles_average,
    candles_sum,
    get_readings_period,
    reading_by_candle,
    reading_count,
    reading_period,
)
from ..utils.candlesticks import validate_candlesticktype
from ..utils.common import round_values
from ..utils.indexing import absindex, valid_index
from ..utils.timeframe import (
    TimeFramesSource,
    convert_timeframe_to_timedelta,
    timedelta_to_str,
)
from . import Reading
from .candle import Candle
from .candle_manager import CandleManager
from .candlestick_type import CandlestickType

T = TypeVar("T")
V = TypeVar("V")


class ChildWhen(str, Enum):
    """When a child indicator is calculated relative to its parent."""

    BEFORE = "before"
    AFTER = "after"
    MANUAL = "manual"


def _normalize_when(when: ChildWhen | str) -> ChildWhen:
    if isinstance(when, ChildWhen):
        return when
    try:
        return ChildWhen(when)
    except ValueError as exc:
        raise InvalidIndicator(
            f"Invalid child when {when!r}; expected one of "
            f"{', '.join(member.value for member in ChildWhen)}"
        ) from exc


@dataclass(kw_only=True)
class Indicator(Generic[V], ABC):
    candles: list[Candle] = field(default_factory=list)
    name: str = ""
    timeframe: TimeFramesSource | None = None
    timeframe_fill: bool = False
    candle_life: timedelta | None = None
    candlestick: CandlestickType | str | None = None
    rounding: int | None = 4

    children: dict[str, Indicator] = field(init=False, default_factory=dict)
    _when: ChildWhen | None = field(init=False, default=None)
    _generated_name: bool = field(init=False, default=False)
    _active_index: int = field(init=False, default=0)

    _name: str = field(init=False, default="")
    _timeframe: timedelta | None = field(init=False)
    _candle_mngr: CandleManager = field(init=False)

    _initialised: bool = field(init=False, default=False)

    def __post_init__(self):
        self._validate_fields()

        self._timeframe = convert_timeframe_to_timedelta(self.timeframe)
        self.timeframe = timedelta_to_str(self._timeframe) if self._timeframe else None

        if self.candlestick is not None:
            self.candlestick = validate_candlesticktype(self.candlestick)

        self.candle_manager = CandleManager(
            self.candles,
            self.candle_life,
            self._timeframe,
            self.timeframe_fill,
            self.candlestick,
        )

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

    def _generate_name(self) -> str:
        return self._name

    @property
    def candle_manager(self) -> CandleManager:
        """The Candle Manager which controls TimeFrame, Trimming and collapsing"""
        return self._candle_mngr

    @candle_manager.setter
    def candle_manager(self, manager: CandleManager):
        """The Candle Manager which controls TimeFrame, Trimming and collapsing,
        this will overwrite the Manager as well as the candles"""
        self._candle_mngr = manager

        self.candles = self._candle_mngr.candles
        self.timeframe = (
            timedelta_to_str(self._candle_mngr.timeframe)
            if self._candle_mngr.timeframe
            else None
        )
        self._timeframe = self._candle_mngr.timeframe
        self.timeframe_fill = self._candle_mngr.timeframe_fill
        self.candle_life = self._candle_mngr.candle_life
        self.candlestick = self._candle_mngr.candlestick
        for indicator in self.children.values():
            indicator.candle_manager = self._candle_mngr

    @property
    def open(self) -> float:
        return self.candles[self._active_index].open

    @property
    def high(self) -> float:
        return self.candles[self._active_index].high

    @property
    def low(self) -> float:
        return self.candles[self._active_index].low

    @property
    def close(self) -> float:
        return self.candles[self._active_index].close

    @property
    def volume(self) -> int:
        return self.candles[self._active_index].volume

    def prev(self, source: Source | None = None, default: T | None = None) -> V | T:
        """Previous reading — shorthand for `prev_reading`."""
        return self.prev_reading(source, default)

    def at(
        self,
        index: int,
        source: Source | None = None,
        default: T | None = None,
    ) -> V | T:
        """Reading at a specific candle index — shorthand for `reading`."""
        return self.reading(source, index=index, default=default)

    def src(self, default: T | None = None) -> V | T:
        """Current reading for this indicator's configured ``source``."""
        return self.reading(getattr(self, "source", "close"), default=default)

    def prev_src(self, default: T | None = None) -> V | T:
        """Previous reading for this indicator's configured ``source``."""
        return self.prev_reading(getattr(self, "source", "close"), default=default)

    def at_src(self, index: int, default: T | None = None) -> V | T:
        """Reading at ``index`` for this indicator's configured ``source``."""
        return self.reading(
            getattr(self, "source", "close"), index=index, default=default
        )

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
            if name in ["candles", "children"]:
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

    def readings(self, name: Source | None = None) -> list[Reading | V]:
        """
        Retrieve the indicator readings for within the candles as a list.

        This method collects the readings of a specified indicator for all candles
        and returns them as a list. If no name is provided, the generated name of
        the indicator is used.

        Args:
            name (str | None): The name of the indicator to retrieve.
                                  Defaults to `self.name` if not provided.

        Returns:
            List[float | dict | None]: A list containing the indicator values for
                                       each candle. The values may be floats,
                                       dictionaries (for complex indicators),
                                       or `None` if no reading is available.
        """
        return self._find_readings(name)  # type: ignore

    def prepend(self, candles: Candles):
        """Prepends a Candle or a chronological ordered list of Candle's to the front of the Indicator Candle's. This will only re-sample and re-calculate the new Candles, with minor overlap.

        Args:
            candles: The Candle or List of Candle's to prepend.
        """
        self._candle_mngr.prepend(candles)
        self.calculate()

    def append(self, candles: Candles):
        """Appends a Candle or a chronological ordered list of Candle's to the end of the Indicator Candle's. This will only re-sample and re-calculate the new Candles, with minor overlap.

        Args:
            candles: The Candle or List of Candle's to append.
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

    @abstractmethod
    def _calculate_reading(self, index: int) -> V: ...

    def _calculate_children(
        self,
        when: ChildWhen,
        index: int,
        end_index: int | None = None,
    ):
        for indicator in self.children.values():
            if indicator._when == when:
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
            self._calculate_children(ChildWhen.BEFORE, index)

            reading = round_values(
                self._calculate_reading(index=index), round_by=self.rounding
            )

            if index < len(self.candles) - 1 and self._reading_dup(
                reading, self.candles[index]
            ):
                break

            self._set_reading(reading, index)
            self._calculate_children(ChildWhen.AFTER, index)

    def _reading_dup(self, reading: Reading | V, candle: Candle) -> bool:
        """Optimisation method for 'calculate'.
        if calculating and not on latest Candle, check if reading match's a pre-existing reading.
        This prevent's it from continuing calculating if already has readings
        It also means if Candles are prepended they will be calculated, and already calculated readings
        will be re-calculated using new prepended candles data until the reading stabilises.
        """
        if reading is None:
            return False
        cur_reading = candle.indicators.get(
            self.name, candle.sub_indicators.get(self.name)
        )

        if cur_reading is None:
            return False

        return reading == cur_reading

    def calculate_index(self, start_index: int, end_index: int | None = None):
        """Calculate the TA values, will calculate a index range the Candles, will re-calculate"""
        self.check_initialised()

        start_index = absindex(start_index, len(self.candles))

        if end_index is not None:
            end_index = absindex(end_index, len(self.candles))
        else:
            end_index = start_index

        for index in range(start_index, end_index + 1):
            self._set_active_index(index)
            self._calculate_children(ChildWhen.BEFORE, index)

            reading = round_values(self._calculate_reading(index=index), self.rounding)

            self._set_reading(reading, index)
            self._calculate_children(ChildWhen.AFTER, index)

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

    def _set_reading(self, reading: V, index: int | None = None):
        index = self._active_index if index is None else index

        if self._when is not None:
            self.candles[index].sub_indicators[self.name] = reading  # type: ignore
        else:
            self.candles[index].indicators[self.name] = reading  # type: ignore

    def _set_active_index(self, index: int):
        self._active_index = index
        for indicator in self.children.values():
            if indicator._when == ChildWhen.MANUAL and isinstance(indicator, Managed):
                indicator.set_active_index(index)

    def add_child(
        self,
        indicator: Indicator,
        when: ChildWhen | str = ChildWhen.BEFORE,
    ) -> Indicator:
        """Register a child indicator that shares this indicator's candles.

        Args:
            indicator: The child indicator to attach.
            when: When the child is calculated relative to the parent at each index.
                :attr:`ChildWhen.BEFORE` runs before `_calculate_reading`.
                :attr:`ChildWhen.AFTER` runs after the parent's reading is stored.
                :attr:`ChildWhen.MANUAL` is only calculated when explicitly invoked
                (e.g. via `Managed.set_reading` or `calculate_index`).
        """
        when = _normalize_when(when)

        if when == ChildWhen.MANUAL:
            if indicator.name == MANAGED_NAME:
                indicator.name = f"{self.name}_data"
            elif indicator._generated_name:
                indicator.name = f"{self.name}-{indicator.name}"
        elif indicator._generated_name:
            indicator.name = f"{self.name}-{indicator.name}"

        indicator._when = when
        indicator.candle_manager = self._candle_mngr
        indicator.rounding = None
        self.children[indicator.name] = indicator
        return indicator

    def add_child_after(self, indicator: Indicator) -> Indicator:
        """Register a child calculated after the parent's reading is stored."""
        return self.add_child(indicator, when=ChildWhen.AFTER)

    def add_child_managed(self, indicator: Indicator) -> Indicator:
        """Register a child calculated only when explicitly invoked."""
        return self.add_child(indicator, when=ChildWhen.MANUAL)

    def add_state(self, name: str | None = None) -> State:
        """Register hidden state storage for incremental calculations."""
        managed = Managed(name=name) if name else Managed()
        return State(self, self.add_child_managed(managed))

    def _find_reading(self, source: Source | None = None, index: int | None = None) -> V:
        if not self.candles:
            return None

        if index is None:
            index = self._active_index
        elif valid_index(index, len(self.candles)):
            index = absindex(index, len(self.candles))
        else:
            return None

        if not source or (isinstance(source, str) and source == self.name):
            return reading_by_candle(self.candles[index], self.name)  # type: ignore
        if isinstance(source, str):
            return reading_by_candle(self.candles[index], source)  # type: ignore
        return reading_by_candle(self.candles[index], source.name)  # type: ignore

    def _find_readings(self, source: Source | None = None) -> list[Reading | V]:
        if not self.candles:
            return []

        if not source:
            name = self.name
            return [reading_by_candle(candle, name) for candle in self.candles]
        if isinstance(source, Indicator):
            name = source.name
            return [reading_by_candle(candle, name) for candle in self.candles]
        if isinstance(source, NestedSource):
            return source.readings()  # type: ignore

        return [reading_by_candle(candle, source) for candle in self.candles]

    def _find_candles(self, source: Source | None = None) -> tuple[list[Candle], str]:
        if not source or (isinstance(source, str) and source == self.name):
            return self.candles, self.name
        if isinstance(source, str):
            return self.candles, source
        return source.candles, source.name

    def exists(self, source: Source | None = None) -> bool:
        value = self._find_reading(source)
        if isinstance(value, dict):
            return any(v is not None for v in value.values())
        return value is not None

    def prev_exists(self, source: Source | None = None) -> bool:
        if self._active_index == 0:
            return False
        value = self._find_reading(source, self._active_index - 1)
        if isinstance(value, dict):
            return any(v is not None for v in value.values())
        return value is not None

    def prev_reading(
        self, source: Source | None = None, default: T | None = None
    ) -> V | T:
        if self._active_index == 0:
            return default  # type: ignore
        value = self._find_reading(source, self._active_index - 1)
        return value if value is not None else default  # type: ignore

    def reading(
        self,
        source: Source | None = None,
        index: int | None = None,
        default: T | None = None,
    ) -> V | T:
        """Simple method to get an indicator reading from the index"""
        value = self._find_reading(source, index)
        return value if value is not None else default  # type: ignore

    def reading_count(
        self, source: Source | None = None, index: int | None = None
    ) -> int:
        """Returns how many instance of the given indicator exist"""
        return reading_count(
            *self._find_candles(source),
            index if index is not None else self._active_index,
        )

    def reading_period(
        self, period: int, source: Source | None = None, index: int | None = None
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
        source: Source | None = None,
        index: int | None = None,
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
        source: Source | None = None,
        index: int | None = None,
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
        source: Source | None = None,
        index: int | None = None,
        include_latest: bool = False,
    ) -> list[float | int]:
        return get_readings_period(
            *self._find_candles(source),
            length,
            index if index is not None else self._active_index,
            include_latest,
        )

    def purge(self):
        """Remove this indicator value from all Candles"""
        self._candle_mngr.purge({self.name} | self.children.keys())

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
    _when: ChildWhen | None = field(init=False, default=ChildWhen.MANUAL)
    _active_index: int = field(default=0)

    def _generate_name(self) -> str:
        return self._name

    def _calculate_reading(self, index: int) -> Reading: ...

    def set_reading(self, reading: Reading, index: int | None = None):  # type: ignore
        if index is None:
            index = self._active_index
        else:
            self.set_active_index(index)

        self._calculate_children(ChildWhen.BEFORE, index)
        self._set_reading(reading, index)  # type: ignore
        self._calculate_children(ChildWhen.AFTER, index)

    def set_active_index(self, index: int):
        self._active_index = index


class State:
    """Internal state backed by a managed child indicator.

    Use via `Indicator.add_state()` rather than constructing directly.
    Dictionary keys map to fields stored on each candle's `sub_indicators`.
    """

    __slots__ = ("_managed", "_parent", "_sources")

    def __init__(self, parent: Indicator, managed: Managed):
        self._parent = parent
        self._managed = managed
        self._sources: dict[str, NestedSource] = {}

    @property
    def managed(self) -> Managed:
        """Underlying managed child, e.g. as an EMA `source`."""
        return self._managed

    def source(self, key: str) -> NestedSource:
        """Reference a state field as an indicator source."""
        if key not in self._sources:
            self._sources[key] = NestedSource(self._managed, key)
        return self._sources[key]

    def prev(self, key: str | None = None, default: T | None = None) -> Reading | T:
        """Previous reading for the whole state or a single field."""
        if key is None:
            return self._parent.prev_reading(self._managed, default)  # type: ignore
        return self._parent.prev_reading(self.source(key), default)  # type: ignore

    def reading(self, key: str | None = None, default: T | None = None) -> Reading | T:
        """Current reading for the whole state or a single field."""
        if key is None:
            value = self._managed.reading()
            return value if value is not None else default  # type: ignore
        return self._parent.reading(self.source(key), default=default)  # type: ignore

    def prev_exists(self, key: str | None = None) -> bool:
        if key is None:
            return self._parent.prev_exists(self._managed)
        return self._parent.prev_exists(self.source(key))

    def exists(self, key: str | None = None) -> bool:
        if key is None:
            return self._managed.exists()
        return self._parent.exists(self.source(key))

    def set(self, reading: Reading, index: int | None = None) -> None:
        """Replace the stored state for the current or given candle."""
        self._managed.set_reading(reading, index=index)  # type: ignore

    def update(self, index: int | None = None, **values: Reading) -> None:
        """Merge fields into dict state for the current or given candle."""
        current = self._parent.reading(self._managed, index=index, default={})
        if isinstance(current, dict):
            self._managed.set_reading({**current, **values}, index=index)  # type: ignore
        else:
            self._managed.set_reading(values, index=index)  # type: ignore


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

    def reading(self, index: int | None = None) -> Reading:  # type: ignore
        value = self.indicator.reading(index=index)
        if isinstance(value, dict):
            return value.get(self.nested_name)  # type: ignore
        return value

    def readings(self) -> list[Reading]:
        return [
            v.get(self.nested_name) if isinstance(v, dict) else v
            for v in self.indicator.readings()
        ]

    def __str__(self):
        return f"{self.indicator.name}.{self.nested_name}"


Source: TypeAlias = str | Indicator | NestedSource
