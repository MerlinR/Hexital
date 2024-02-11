from __future__ import annotations

from abc import ABC, abstractmethod
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import timedelta
from typing import Dict, List, Optional

from hexital.analysis import movement, patterns
from hexital.core.candle import Candle
from hexital.core.candle_manager import CandleManager
from hexital.core.candlestick_type import CandlestickType
from hexital.utils.candles import (
    candles_sum,
    reading_by_candle,
    reading_count,
    reading_period,
)
from hexital.utils.candlesticks import validate_candlesticktype
from hexital.utils.indexing import round_values
from hexital.utils.timeframe import TimeFrame, validate_timeframe


@dataclass(kw_only=True)
class Indicator(ABC):
    candles: List[Candle] = field(default_factory=list)
    fullname_override: Optional[str] = None
    name_suffix: Optional[str] = None
    round_value: int = 4
    timeframe: Optional[str | TimeFrame] = None
    timeframe_fill: bool = False
    candles_lifespan: Optional[timedelta] = None
    candlestick_type: Optional[CandlestickType | str] = None

    _name: str = field(init=False, default="")
    _output_name: str = field(init=False, default="")
    _candles: CandleManager = field(init=False, default_factory=CandleManager)
    _sub_indicators: List[Indicator] = field(init=False, default_factory=list)
    _managed_indicators: Dict[str, Managed | Indicator] = field(init=False, default_factory=dict)
    _sub_indicator: bool = field(init=False, default=False)
    _active_index: int = field(init=False, default=0)
    _initialised: bool = field(init=False, default=False)

    def __post_init__(self):
        self._validate_fields()

        if self.timeframe is not None:
            self.timeframe = validate_timeframe(self.timeframe)

        if self.candlestick_type is not None:
            self.candlestick_type = validate_candlesticktype(self.candlestick_type)

        self._candles = CandleManager(
            self.candles,
            self.candles_lifespan,
            self.timeframe,
            self.timeframe_fill,
            self.candlestick_type,
        )

        self.candles = self._candles.candles

        self._internal_generate_name()

    def __str__(self):
        data = vars(self)
        data.pop("candles")
        data["name"] = data["_output_name"]
        return str(data)

    def _internal_generate_name(self):
        name = ""
        if self.fullname_override:
            name = self.fullname_override
        else:
            name = self._generate_name()
            if self.timeframe:
                name += f"_{self._candles.timeframe}"

        if self.name_suffix:
            name += f"_{self.name_suffix}"

        self._output_name = self._sanitise_name(name)

    def _initialise(self):
        return

    def _validate_fields(self):
        return

    @abstractmethod
    def _generate_name(self) -> str:
        ...

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
        self.timeframe = manager.timeframe
        self.timeframe_fill = manager.timeframe_fill
        self.candles_lifespan = manager.candles_lifespan
        self.candlestick_type = manager.candlestick_type

    @property
    def name(self) -> str:
        """The indicator name that will be saved into the Candles"""
        return self._output_name

    @property
    def has_reading(self) -> bool:
        """Simple boolean to state if values are being generated yet in the candles"""
        if len(self.candles) == 0:
            return False
        return self.reading(index=-1) is not None

    @property
    def settings(self) -> dict:
        """Returns a dict format of how this indicator can be generated"""
        output = {"indicator": self._name if self._name else type(self).__name__}

        for name, value in self.__dict__.items():
            if name == "candles":
                continue
            if name == "timeframe_fill" and self.timeframe is None:
                continue

            if name == "candlestick_type" and value:
                output[name] = value.minimal_name
            elif not name.startswith("_") and value is not None:
                output[name] = deepcopy(value)

        return output

    def as_list(self, name: Optional[str] = None) -> List[float | dict | None]:
        """Gathers the indicator for all candles as a list
        E.G `EMA_12` OR `MACD_12_26_9.MACD`"""
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

    def _calculate_reading(self, index: int) -> float | dict | None:
        pass

    def calculate(self):
        """Calculate the TA values, will calculate for all the Candles,
        where this indicator is missing"""
        if not self._initialised:
            self._initialise()
            self._initialised = True

        for indicator in self._sub_indicators:
            indicator.calculate()

        for index in range(self._find_calc_index(), len(self.candles)):
            self._set_active_index(index)

            if self.candles[index].indicators.get(self.name) is not None:
                continue

            reading = round_values(self._calculate_reading(index=index), round_by=self.round_value)
            self._set_reading(reading, index)

    def calculate_index(self, start_index: int, end_index: Optional[int] = None):
        """Calculate the TA values, will calculate a index range the Candles, will re-calculate"""
        end_index = end_index if end_index else start_index + 1

        for index in range(start_index, end_index):
            self._set_active_index(index)
            reading = round_values(self._calculate_reading(index=index), round_by=self.round_value)
            self._set_reading(reading, index)

    def _find_calc_index(self) -> int:
        """Optimisation method, to find where to start calculating the indicator from
        Searches from newest to oldest to find the first candle without the indicator
        """
        if len(self.candles) == 0 or self.name not in self.candles[0].indicators:
            return 0

        for index in range(len(self.candles) - 1, 0, -1):
            if self.name in self.candles[index].indicators:
                return index + 1
            elif self.name in self.candles[index].sub_indicators:
                return index + 1

        return len(self.candles) - 1

    def _set_active_index(self, index: int):
        self._active_index = index

        for indicator in self._managed_indicators.values():
            if isinstance(indicator, Managed):
                indicator.set_active_index(index)

    def _add_sub_indicator(self, indicator: Indicator):
        """Adds sub indicator, this will auto calculate with indicator"""
        indicator._sub_indicator = True
        indicator.candle_manager = self._candles
        self._sub_indicators.append(indicator)

    def _add_managed_indicator(self, name: str, indicator: Managed | Indicator):
        """Adds managed sub indicator, this will not auto calculate with indicator"""
        indicator._sub_indicator = True
        indicator.candle_manager = self._candles
        self._managed_indicators[name] = indicator

    def prev_exists(self) -> bool:
        return self.prev_reading(self.name) is not None

    def prev_reading(self, name: Optional[str] = None) -> float | dict | None:
        if len(self.candles) == 0 or self._active_index == 0:
            return None
        return self.reading(name=name if name else self.name, index=self._active_index - 1)

    def reading(
        self, name: Optional[str] = None, index: Optional[int] = None
    ) -> float | dict | None:
        """Simple method to get an indicator reading from the index
        Name can use '.' to find nested reading, E.G 'MACD_12_26_9.MACD"""
        return reading_by_candle(
            self.candles[index if index is not None else self._active_index],
            name if name else self.name,
        )

    def read_candle(self, candle: Candle, name: Optional[str] = None) -> float | dict | None:
        """Simple method to get an indicator reading from a candle,
        regardless of it's location"""
        return reading_by_candle(candle, name if name else self.name)

    def reading_count(self, name: Optional[str] = None) -> int:
        """Returns how many instance of the given indicator exist"""
        return reading_count(self.candles, name if name else self.name)

    def reading_period(
        self, period: int, name: Optional[str] = None, index: Optional[int] = None
    ) -> bool:
        """Will return True if the given indicator goes back as far as amount,
        It's true if exactly or more than. Period will be period -1"""
        return reading_period(
            self.candles,
            period=period,
            name=name if name else self.name,
            index=index if index else self._active_index,
        )

    def candles_sum(
        self, length: int = 1, name: Optional[str] = None, index: Optional[int] = None
    ) -> float | None:
        return candles_sum(
            self.candles,
            name if name else self.name,
            length,
            index if index is not None else self._active_index,
        )

    def purge(self):
        """Remove this indicator value from all Candles"""
        self._candles.purge(
            {self.name}
            | {indicator.name for indicator in self._sub_indicators}
            | {indicator.name for indicator in self._managed_indicators.values()}
        )

    def recalculate(self):
        """Re-calculate this indicator value for all Candles"""
        self.purge()
        self.calculate()

    def rising(self, name: Optional[str] = None, length: int = 4, index: int = -1) -> bool:
        return movement.rising(self.candles, name if name else self.name, length, index)

    def falling(self, name: Optional[str] = None, length: int = 4, index: int = -1) -> bool:
        return movement.falling(self.candles, name if name else self.name, length, index)

    def mean_rising(self, name: Optional[str] = None, length: int = 4, index: int = -1) -> bool:
        return movement.mean_rising(self.candles, name if name else self.name, length, index)

    def mean_falling(self, name: Optional[str] = None, length: int = 4, index: int = -1) -> bool:
        return movement.mean_falling(self.candles, name if name else self.name, length, index)

    def highest(self, name: Optional[str] = None, length: int = 4, index: int = -1) -> float:
        return movement.highest(self.candles, name if name else self.name, length, index)

    def lowest(self, name: Optional[str] = None, length: int = 4, index: int = -1) -> float:
        return movement.lowest(self.candles, name if name else self.name, length, index)

    def highestbar(
        self, name: Optional[str] = None, length: int = 4, index: int = -1
    ) -> int | None:
        return movement.highestbar(self.candles, name if name else self.name, length, index)

    def lowestbar(
        self, name: Optional[str] = None, length: int = 4, index: int = -1
    ) -> int | None:
        return movement.lowestbar(self.candles, name if name else self.name, length, index)

    def doji(
        self,
        length: int = 10,
        lookback: Optional[int] = None,
        asint: bool = False,
        index: Optional[int] = None,
    ) -> bool | int:
        return patterns.doji(
            self.candles, length=length, lookback=lookback, asint=asint, index=index
        )

    def hammer(
        self,
        length: int = 10,
        lookback: Optional[int] = None,
        asint: bool = False,
        index: Optional[int] = None,
    ) -> bool | int:
        return patterns.hammer(
            self.candles, length=length, lookback=lookback, asint=asint, index=index
        )


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

    def set_reading(self, reading: float | dict, index: Optional[int] = None):
        if index is None:
            index = self._active_index
        else:
            self.set_active_index(index)
        self._set_reading(reading, self._active_index)

    def set_active_index(self, index: int):
        self._active_index = index
