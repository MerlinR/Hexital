from __future__ import annotations

from abc import ABC, abstractmethod
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import timedelta
from typing import Dict, List, Optional

from hexital.core.candle import Candle
from hexital.lib.candle_extension import (
    TimeFrame,
    multi_convert_candles,
    trim_candles,
    reading_as_list,
    collapse_candles_timeframe,
    reading_count,
    reading_by_candle,
    candles_sum,
    reading_period,
)
from hexital.lib.utils import round_values


@dataclass(kw_only=True)
class Indicator(ABC):
    candles: List[Candle] = field(default_factory=list)
    fullname_override: Optional[str] = None
    name_suffix: Optional[str] = None
    round_value: int = 4
    timeframe: Optional[str | TimeFrame] = None
    timeframe_fill: bool = False
    candles_lifespan: Optional[timedelta] = None
    _output_name: str = ""
    _sub_indicators: List[Indicator] = field(default_factory=list)
    _managed_indicators: Dict[str, Indicator] = field(default_factory=dict)
    _sub_indicator: bool = False
    _active_index: int = 0
    _initialised: bool = False

    def __post_init__(self):
        self._validate_fields()

        if self.timeframe:
            if isinstance(self.timeframe, str):
                self.timeframe = self.timeframe.upper()
            if self.candles:
                self.candles = deepcopy(self.candles)

        self._collapse_candles()
        trim_candles(self.candles, self.candles_lifespan)
        self._internal_generate_name()

    def __str__(self):
        data = vars(self)
        data.pop("candles")
        data["name"] = data["_output_name"]
        return str(data)

    def _internal_generate_name(self):
        if self.fullname_override:
            self._output_name = self.fullname_override
        else:
            self._output_name = self._generate_name()
            if self.timeframe:
                if isinstance(self.timeframe, str):
                    self._output_name += f"_{self.timeframe}"
                else:
                    self._output_name += f"_{self.timeframe.value}"

        if self.name_suffix:
            self._output_name += f"_{self.name_suffix}"

    def _initialise(self):
        pass

    def _validate_fields(self):
        pass

    @abstractmethod
    def _generate_name(self) -> str:
        pass

    @property
    def name(self) -> str:
        """The indicator name that will be saved into the Candles"""
        return self._output_name

    @property
    def read(self) -> float | dict | None:
        """Get's this newest reading of this indicator"""
        return self.reading()

    @property
    def as_list(self) -> List[float | dict | None]:
        """Gathers the indicator for all candles as a list"""
        return reading_as_list(self.candles, self.name)

    @property
    def has_reading(self) -> bool:
        """Simple boolean to state if values are being generated yet in the candles"""
        if len(self.candles) == 0:
            return False
        return self.reading(index=-1) is not None

    @property
    def settings(self) -> dict:
        """Returns a dict format of how this indicator can be generated"""
        output = {"indicator": type(self).__name__}

        for name, value in self.__dict__.items():
            if name == "candles":
                continue
            if name == "timeframe_fill" and self.timeframe is None:
                continue
            if not name.startswith("_") and value is not None:
                output[name] = deepcopy(value)

        return output

    def _set_reading(self, reading: float | dict | None, index: Optional[int] = None):
        if index is None:
            index = self._active_index

        if self._sub_indicator:
            self.candles[index].sub_indicators[self.name] = reading
        else:
            self.candles[index].indicators[self.name] = reading

    def append(self, candles: Candle | List[Candle] | dict | List[dict] | list | List[list]):
        candles_ = multi_convert_candles(candles)

        if self.timeframe:
            self.candles.extend(deepcopy(candles_))
        else:
            self.candles.extend(candles_)

        self._collapse_candles()
        self.calculate()
        trim_candles(self.candles, self.candles_lifespan)

    def _calculate_reading(self, index: int) -> float | dict | None:
        pass

    def _collapse_candles(self):
        if self.timeframe:
            self.candles.extend(
                collapse_candles_timeframe(self.candles, self.timeframe, self.timeframe_fill)
            )

    def calculate(self):
        """Calculate the TA values, will calculate for all the Candles,
        where this indicator is missing"""
        if not self._initialised:
            self._initialise()
            self._initialised = True

        for indicator in self._sub_indicators:
            indicator.calculate()

        for index in range(self._find_calc_index(), len(self.candles)):
            self._set_index(index)
            if self.reading(index=index) is None:
                reading = round_values(
                    self._calculate_reading(index=index), round_by=self.round_value
                )
                self._set_reading(reading, index)

    def calculate_index(self, start_index: int, end_index: Optional[int] = None):
        """Calculate the TA values, will calculate a index range the Candles"""
        end_index = end_index if end_index else start_index + 1

        for index in range(start_index, end_index):
            self._set_index(index)
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
        return 0

    def _set_index(self, index: int):
        self._active_index = index

        for indicator in self._managed_indicators.values():
            set_indicator_index = getattr(indicator, "set_active_index", None)
            if callable(set_indicator_index):
                set_indicator_index(index)

    def _add_sub_indicator(self, indicator: Indicator):
        """Adds sub indicator, this will auto calculate with indicator"""
        indicator._sub_indicator = True
        self._sub_indicators.append(indicator)

    def _add_managed_indicator(self, name: str, indicator: Indicator):
        """Adds managed sub indicator, this will not auto calculate with indicator"""
        indicator._sub_indicator = True
        self._managed_indicators[name] = indicator

    def _managed_indictor(self, name: str) -> Indicator | None:
        return self._managed_indicators.get(name)

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
        for candle in self.candles:
            candle.indicators.pop(self.name, None)
            for indicator in self._sub_indicators:
                candle.sub_indicators.pop(indicator.name, None)
            for indicator in self._managed_indicators.values():
                candle.sub_indicators.pop(indicator.name, None)

    def recalculate(self):
        """Re-calculate this indicator value for all Candles"""
        self.purge()
        self.calculate()
