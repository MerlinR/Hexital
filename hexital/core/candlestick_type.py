from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import List, Optional

from hexital.core.candle import Candle
from hexital.utils.common import CalcMode
from hexital.utils.indexing import valid_index
from hexital.utils.weakreflist import WeakList


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
        if mode == CalcMode.INSERT:
            start_index = 0
        elif index is not None:
            start_index = index
        else:
            start_index = self._find_transform_index()

        self._derived_idx = len(self.derived_candles) if mode == CalcMode.APPEND else 0

        if mode == CalcMode.INSERT:
            self.derived_candles.reset()

        for index in range(start_index, len(self.candles)):
            candle = self.candles[index]

            candles = self.transform_candle(candle)

            # None Candles never added to derived
            if not candles:
                candle.refs[self.acronym] = None
                continue

            if candles := self._insert_derived_candles(candles):
                candle.refs[self.acronym] = candles
            else:
                break

    def _insert_derived_candles(self, candles: Candle | Sequence[Candle]) -> Sequence:
        candle_ = candles if isinstance(candles, Sequence) else [candles]

        for cdl in candle_:
            cdl.tag = self.acronym

            if (
                valid_index(self._derived_idx, len(self.derived_candles))
                and cdl == self.derived_candles[self._derived_idx]
            ):
                return []

            self.derived_candles.insert(self._derived_idx, cdl)
            self._derived_idx += 1

        return candle_

    def _find_transform_index(self) -> int:
        """Optimisation method, to find where to start calculating the indicator from
        Searches from newest to oldest to find the first candle without the indicator
        """
        if not self.candles or not self.candles[0].refs.get(self.acronym):
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
