from collections.abc import Sequence
from dataclasses import dataclass, field

from ..core.candlestick_type import CandlestickType
from ..utils.candles import Candle

RENKO_OPTIONS = ["brick", "atr", "perc"]


@dataclass(kw_only=True)
class Renko(CandlestickType):
    """Renko
    There are tree ways to build the bricks:

        - Bricks - The Renko bricks are build as a fixed amount, this is, for each 5$ of increase or decrease in the price a new brick is built
        - Percentage - The Renko bricks are build based on a percentage, this is, if this parameter is set to 0.02 (2%) and the price increase (or decrease) 2%, a new brick is built
        - ATR - The Renko bricks are build based on the average true value (ATR). For every candlestick, the ATR is computed and then this values is used to determine if it is need to create another brick or not

    """

    name: str = "Renko"
    acronym: str = "RENKO"
    # candles: List[Candle]  # Fresh Candles
    # derived_candles: WeakList[Candle]  # Transformed Candles

    mode: str = field(default="brick")
    size: float = field(default=5)

    def _validate_fields(self):
        if self.mode not in RENKO_OPTIONS:
            raise TypeError(f"Renko Mode must be one of {RENKO_OPTIONS}")

    def transform_candle(self, candle: Candle) -> None | Candle | Sequence[Candle]:
        if self.mode == "brick":
            return self._brick(candle)

    def _brick(self, candle: Candle) -> None | Candle | Sequence[Candle]:
        if prev_candle := self.prev_derived():
            candles = []
            _close = prev_candle.close

            bricks = int(abs(prev_candle.close - candle.close) // self.size)

            if _close - candle.close < self.size:
                for i in range(bricks):
                    open_ = _close + (0 if not i else (self.size * (1 + i)))
                    close_ = open_ + self.size
                    candles.append(
                        Candle(open_, open_, close_, close_, int(candle.volume / bricks))
                    )
            elif _close - candle.close > self.size:
                for i in range(bricks):
                    open_ = _close - (0 if not i else (self.size * (1 + i)))
                    close_ = open_ - self.size
                    candles.append(
                        Candle(open_, open_, close_, close_, int(candle.volume / bricks))
                    )

            return candles
        init_close = float(candle.close // self.size) * self.size
        open_ = init_close - self.size if candle.positive else init_close + self.size
        return Candle(open_, open_, init_close, init_close, candle.volume)
