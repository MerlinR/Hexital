from abc import ABC, abstractmethod
from collections.abc import Sequence
from enum import Enum, auto
from typing import List, Optional

from hexital.core.candle import Candle
from hexital.utils.weakreflist import WeakList


class CalcMode(Enum):
    INSERT = auto()
    APPEND = auto()
    PREPEND = auto()


class CandlestickType(ABC):
    name: str = "NA"
    acronym: str = "NA"

    candles: List[Candle]  # Fresh Candles
    derived_candles: WeakList[Candle]  # Transformed Candles # List[ReferenceType[Candle]

    _derived_idx: int = 0

    def __init__(self, candles: Optional[List[Candle]] = None):
        self.candles = candles if candles else []
        self.derived_candles = WeakList()

    def set_candle_refs(self, candles: List[Candle]):
        """Replace CandlestickType Candles to own by reference"""
        self.candles = candles

    @property
    def index(self) -> int:
        """Current derived_candles index off calculation"""
        return self._derived_idx

    @abstractmethod
    def transform_candle(self, candle: Candle) -> None | Candle | Sequence[Candle]: ...

    def transform(self, mode: CalcMode = CalcMode.INSERT, index: Optional[int] = None):
        """Transforms the Candle's into their candlestick type, using the given CalcMode.
        INSERT: Fresh transformation, will re-transform all Candles. Slow
        APPEND: Will transform all Candles at the end that have no derived Candles
        PREPEND: Will transform all Candles from the start until hitting already Transformed candles
        """
        if mode != CalcMode.APPEND:
            start_index = 0
        else:
            start_index = index if index is not None else self._find_transform_index()

        self._derived_idx = 0 if mode != CalcMode.APPEND else len(self.derived_candles)

        if mode == CalcMode.INSERT:
            self.derived_candles.reset()

        for index in range(start_index, len(self.candles)):
            candle = self.candles[index]

            if mode == CalcMode.PREPEND and self.acronym in candle.refs:
                break

            trans_cdl = self.transform_candle(candle)

            # None Candles never added to derived
            if not trans_cdl:
                candle.refs[self.acronym] = None
                continue

            for cdl in trans_cdl if isinstance(trans_cdl, Sequence) else [trans_cdl]:
                cdl.tag = self.acronym

                if mode != CalcMode.PREPEND:
                    self.derived_candles.append(cdl)
                else:
                    self.derived_candles.insert(self._derived_idx, cdl)

                self._derived_idx += 1

            candle.refs[self.acronym] = trans_cdl

    def _find_transform_index(self) -> int:
        """Optimisation method, to find where to start calculating the indicator from
        Searches from newest to oldest to find the first candle without the indicator
        """
        if not self.candles:
            return 0

        for index in range(len(self.candles) - 1, -1, -1):
            if self.acronym in self.candles[index].refs:
                return index + 1
        return 0

    def prev_derived(self, index: Optional[int] = None) -> Candle | None:
        """Returns the previous derived Candle"""
        if not self.derived_candles:
            return None

        if index is not None:
            return self.derived_candles[index]

        if self._derived_idx == 0:
            return None

        return self.derived_candles[self._derived_idx - 1]
