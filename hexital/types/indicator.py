from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from hexital.types.ohlcv import OHLCV
from hexital.utilities import ohlcv, utils


@dataclass(kw_only=True)
class Indicator(ABC):
    candles: List[OHLCV] = field(default_factory=list)
    indicator_name: str = None
    fullname_override: str = None
    name_suffix: str = None
    round_value: int = 4
    _output_name: str = ""
    _sub_indicators: List[Indicator] = field(default_factory=list)
    _managed_indicators: Dict[str, Indicator] = field(default_factory=dict)
    _sub_indicator: bool = False
    _active_index: int = 0

    def __post_init__(self):
        self._validate_fields()
        self._internal_generate_name()
        self._initialise()

    def __str__(self):
        data = vars(self)
        data.pop("candles")
        data["name"] = data["_output_name"]
        return str(data)

    def _internal_generate_name(self):
        if self.fullname_override:
            self._output_name = self.fullname_override
        elif self.fullname_override and self.name_suffix:
            self._output_name = f"{self.fullname_override}_{self.name_suffix}"
        elif self.name_suffix:
            self._output_name = f"{self._generate_name()}_{self.name_suffix}"
        else:
            self._output_name = self._generate_name()

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
    def read(self) -> float | dict:
        """Get's this newest reading of this indicator"""
        return self.candles[-1][self._output_name]

    @property
    def as_list(self) -> List[float | dict]:
        """Gathers the indicator for all candles as a list"""
        return ohlcv.reading_as_list(self.candles, self.name)

    @property
    def sub_indicator(self) -> Indicator:
        return self._sub_indicator

    @sub_indicator.setter
    def sub_indicator(self, value: bool):
        self._sub_indicator = value

    @property
    def has_reading(self) -> bool:
        """Simple boolean to state if values are being generated yet in the candles"""
        if len(self.candles) == 0:
            return False
        return self.reading(index=-1) is not None

    def _set_reading(self, index: int, reading: float | dict):
        if self.sub_indicator:
            self.candles[index].sub_indicators[self.name] = reading
        else:
            self.candles[index].indicators[self.name] = reading

    def append(self, candles: OHLCV | List[OHLCV]):
        if isinstance(candles, OHLCV):
            self.candles.append(candles)
        if isinstance(candles, list):
            if isinstance(candles[0], OHLCV):
                self.candles.append(candles)
            else:
                raise TypeError
        else:
            raise TypeError
        self.calculate()

    def _calculate_reading(self, index: int = -1) -> float | dict | None:
        pass

    def calculate(self):
        """Calculate the TA values, will calculate for all the Candles,
        where this indicator is missing"""
        for indicator in self._sub_indicators:
            indicator.calculate()

        for index in range(self._find_calc_index(), len(self.candles)):
            self._set_index(index)
            if self.reading(index=index) is None:
                reading = utils.round_values(
                    self._calculate_reading(index=index), round_by=self.round_value
                )
                self._set_reading(index, reading)

    def calculate_index(self, start_index: int, end_index: Optional[int] = None):
        """Calculate the TA values, will calculate a index range the Candles"""
        end_index = end_index if end_index else start_index + 1
        for index in range(start_index, end_index):
            self._set_index(index)
            reading = utils.round_values(
                self._calculate_reading(index=index), round_by=self.round_value
            )
            self._set_reading(index, reading)

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
            try:
                indicator.set_active_index(index)
            except AttributeError:
                # Due to a managed Indicator, such as a self controlled EMA(MACD)
                pass

    def add_sub_indicator(self, indicator: Indicator):
        """Adds sub indicator, this will auto calculate with indicator"""
        indicator.sub_indicator = True
        self._sub_indicators.append(indicator)

    def add_managed_indicator(self, name: str, indicator: Indicator):
        """Adds managed sub indicator, this will not auto calculate with indicator"""
        indicator.sub_indicator = True
        self._managed_indicators[name] = indicator

    def managed_indictor(self, name: str) -> Indicator:
        return self._managed_indicators.get(name)

    def prev_exists(self) -> bool:
        return self.prev_reading(self.name) is not None

    def prev_reading(self, name: Optional[str] = None) -> float | dict | None:
        if len(self.candles) == 0 or self._active_index == 0:
            return None
        name = name if name else self.name
        return self.reading(name, index=self._active_index - 1)

    def reading(
        self, name: Optional[str] = None, index: Optional[int] = None
    ) -> float | dict | None:
        """Simple method to get an indicator reading from the index
        Name can use '.' to find nested reading, E.G 'MACD_12_26_9.MACD"""
        return ohlcv.reading_by_candle(
            self.candles[index if index is not None else self._active_index],
            name if name else self.name,
        )

    def read_candle(
        self, candle: OHLCV, name: Optional[str] = None
    ) -> float | dict | None:
        """Simple method to get an indicator reading from a candle,
        regardless of it's location"""
        return ohlcv.reading_by_candle(
            candle,
            name if name else self.name,
        )

    def reading_count(self, name: Optional[str] = None) -> int:
        """Returns how many instance of the given indicator exist"""
        return ohlcv.reading_count(
            self.candles,
            name if name else self.name,
        )

    def reading_period(
        self, period: int, name: Optional[str] = None, index: Optional[int] = None
    ) -> bool:
        """Will return True if the given indicator goes back as far as amount,
        It's true if exactly or more than. Period will be period -1"""
        return ohlcv.reading_period(
            self.candles,
            period=period,
            name=name if name else self.name,
            index=index if index else self._active_index,
        )

    def candles_sum(
        self, length: int = 1, name: Optional[str] = None, index: Optional[int] = None
    ) -> float:
        return utils.candles_sum(
            self.candles,
            name if name else self.name,
            length,
            index if index is not None else self._active_index,
        )

    def purge(self):
        """Remove this indicator value from all Candles"""
        for candle in self.candles:
            candle.indicators.pop(self.name, None)
            candle.sub_indicators.pop(self.name, None)

    def recalculate(self):
        """Re-calculate this indicator value for all Candles"""
        self.purge()
        self.calculate()
