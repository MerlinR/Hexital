from __future__ import annotations

from abc import ABC, abstractmethod
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import timedelta
from typing import Dict, List, Optional, TypeVar

from hexital.core.candle import Candle
from hexital.core.candle_manager import CandleManager
from hexital.core.candlestick_type import CandlestickType
from hexital.utils.candles import (
    candles_average,
    candles_sum,
    get_readings_period,
    reading_by_candle,
    reading_count,
    reading_period,
)
from hexital.utils.candlesticks import validate_candlesticktype
from hexital.utils.indexing import round_values
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

        self._internal_generate_name()

    def __str__(self):
        data = vars(self)
        data.pop("candles")
        return str(data)

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
        self.timeframe = timedelta_to_str(manager.timeframe) if manager.timeframe else None
        self._timeframe = manager.timeframe
        self.timeframe_fill = manager.timeframe_fill
        self.candle_life = manager.candle_life
        self.candlestick = manager.candlestick

    @property
    def has_reading(self) -> bool:
        """
        Check if the indicator has generated values in the candles.

        This property determines whether the indicator readings have been generated
        for the associated candle data.

        Returns:
            bool: `True` if the indicator readings exist in the candles; otherwise, `False`.
        """
        if len(self.candles) == 0:
            return False
        return self.exists(self.name)

    @property
    def prior_calc(self) -> bool:
        if self._sub_indicator and self._sub_calc_prior:
            return True
        return False

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
        output = {"indicator": self._name if self._name else type(self).__name__}

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
                output[name] = deepcopy(value)

        return output

    def as_list(self, name: Optional[str] = None) -> List[float | dict | None]:
        """
        Retrieve the indicator values for all candles as a list.

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
        return [reading_by_candle(candle, name if name else self.name) for candle in self.candles]

    def _set_reading(self, reading: float | dict | None, index: Optional[int] = None):
        index = index if index else self._active_index

        if self._sub_indicator:
            self.candles[index].sub_indicators[self.name] = reading
        else:
            self.candles[index].indicators[self.name] = reading

    def append(self, candles: Candle | List[Candle] | dict | List[dict] | list | List[list]):
        self._candles.append(candles)
        self.calculate()

    @abstractmethod
    def _calculate_reading(self, index: int) -> float | dict | None: ...

    def _calculate_sub_indicators(
        self,
        prior_calc: bool = True,
        start_index: Optional[int] = None,
        end_index: Optional[int] = None,
    ):
        for indicator in self.sub_indicators.values():
            if indicator.prior_calc == prior_calc:
                if start_index and end_index:
                    indicator.calculate_index(start_index, end_index)
                else:
                    indicator.calculate()

    def calculate(self):
        """Calculate the TA values, will calculate for all the Candles,
        where this indicator is missing"""
        if not self._initialised:
            self._initialise()
            self._initialised = True

        self._calculate_sub_indicators(prior_calc=True)

        for index in range(self._find_calc_index(), len(self.candles)):
            self._set_active_index(index)

            if self.candles[index].indicators.get(self.name) is not None:
                continue

            reading = round_values(self._calculate_reading(index=index), round_by=self.rounding)
            self._set_reading(reading, index)

        self._calculate_sub_indicators(prior_calc=False)

    def calculate_index(self, start_index: int, end_index: Optional[int] = None):
        """Calculate the TA values, will calculate a index range the Candles, will re-calculate"""
        end_index = end_index if end_index else start_index + 1

        self._calculate_sub_indicators(True, start_index, end_index)

        for index in range(start_index, end_index):
            self._set_active_index(index)
            reading = round_values(self._calculate_reading(index=index), round_by=self.rounding)
            self._set_reading(reading, index)

        self._calculate_sub_indicators(False, start_index, end_index)

    def _find_calc_index(self) -> int:
        """Optimisation method, to find where to start calculating the indicator from
        Searches from newest to oldest to find the first candle without the indicator
        """
        if len(self.candles) == 0 or (
            self.name not in self.candles[0].indicators
            and self.name not in self.candles[0].sub_indicators
        ):
            return 0

        for index in range(len(self.candles) - 1, 0, -1):
            if (
                self.name in self.candles[index].indicators
                or self.name in self.candles[index].sub_indicators
            ):
                return index + 1

        return 0

    def _set_active_index(self, index: int):
        self._active_index = index
        for indicator in self.managed_indicators.values():
            if isinstance(indicator, Managed):
                indicator.set_active_index(index)

    def add_sub_indicator(self, indicator: Indicator, prior_calc: bool = True):
        """Adds sub indicator, this will auto calculate with indicator"""
        indicator._sub_indicator = True
        indicator._sub_calc_prior = prior_calc
        indicator.candle_manager = self._candles
        indicator.rounding = None
        self.sub_indicators[indicator.name] = indicator

    def add_managed_indicator(self, name: str, indicator: Managed | Indicator):
        """Adds managed sub indicator, this will not auto calculate with indicator"""
        indicator._sub_indicator = True
        indicator.candle_manager = self._candles
        indicator.rounding = None
        self.managed_indicators[name] = indicator

    def exists(self, name: Optional[str] = None) -> bool:
        value = self.reading(self.name if not name else name)
        if isinstance(value, dict):
            return any(v is not None for v in value.values())
        return value is not None

    def prev_exists(self, name: Optional[str] = None) -> bool:
        value = self.prev_reading(self.name if not name else name)
        if isinstance(value, dict):
            return any(v is not None for v in value.values())
        return value is not None

    def prev_reading(
        self, name: Optional[str] = None, default: Optional[T] = None
    ) -> float | dict | None | T:
        if len(self.candles) == 0 or self._active_index == 0:
            return default
        value = self.reading(name=name if name else self.name, index=self._active_index - 1)
        return value if value is not None else default

    def reading(
        self,
        name: Optional[str] = None,
        index: Optional[int] = None,
        default: Optional[T] = None,
    ) -> float | dict | None | T:
        """Simple method to get an indicator reading from the index
        Name can use '.' to find nested reading, E.G 'MACD_12_26_9.MACD"""
        value = reading_by_candle(
            self.candles[index if index is not None else self._active_index],
            name if name else self.name,
        )
        return value if value is not None else default

    def read_candle(
        self,
        candle: Candle,
        name: Optional[str] = None,
        default: Optional[T] = None,
    ) -> float | dict | None | T:
        """Simple method to get an indicator reading from a candle,
        regardless of it's location"""
        value = reading_by_candle(candle, name if name else self.name)
        return value if value is not None else default

    def reading_count(self, name: Optional[str] = None, index: Optional[int] = None) -> int:
        """Returns how many instance of the given indicator exist"""
        return reading_count(
            self.candles,
            name=name if name else self.name,
            index=index if index is not None else self._active_index,
        )

    def reading_period(
        self, period: int, name: Optional[str] = None, index: Optional[int] = None
    ) -> bool:
        """Will return True if the given indicator goes back as far as amount,
        It's true if exactly or more than. Period will be period -1"""
        return reading_period(
            self.candles,
            period=period,
            name=name if name else self.name,
            index=index if index is not None else self._active_index,
        )

    def candles_sum(
        self,
        length: int = 1,
        name: Optional[str] = None,
        index: Optional[int] = None,
        include_latest: bool = True,
    ) -> float | None:
        return candles_sum(
            self.candles,
            name if name else self.name,
            length,
            index if index is not None else self._active_index,
            include_latest,
        )

    def candles_average(
        self,
        length: int = 1,
        name: Optional[str] = None,
        index: Optional[int] = None,
        include_latest: bool = True,
    ) -> float | None:
        return candles_average(
            self.candles,
            name if name else self.name,
            length,
            index if index is not None else self._active_index,
            include_latest,
        )

    def get_readings_period(
        self,
        length: int = 1,
        name: Optional[str] = None,
        index: Optional[int] = None,
        include_latest: bool = False,
    ) -> List[float | int]:
        return get_readings_period(
            self.candles,
            name if name else self.name,
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


@dataclass(kw_only=True)
class Managed(Indicator):
    """Managed

    Empty Indicator thats manually controlled and the reading manually set.

    """

    indicator_name: str = "MAN"
    _sub_indicator: bool = True
    _active_index: int = 0

    def _generate_name(self) -> str:
        return self.indicator_name

    def _calculate_reading(self, index: int) -> float | dict | None: ...

    def set_reading(self, reading: float | dict, index: Optional[int] = None):
        if index is None:
            index = self._active_index
        else:
            self.set_active_index(index)

        self._calculate_sub_indicators(True, index, index + 1)
        self._set_reading(reading, self._active_index)
        self._calculate_sub_indicators(False, index, index + 1)

    def set_active_index(self, index: int):
        self._active_index = index
