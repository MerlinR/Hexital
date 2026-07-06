from dataclasses import dataclass, field

from ..analysis.utils import highest, lowest
from ..core.indicator import Indicator
from .atr import ATR


@dataclass(kw_only=True)
class ChandelierExit(Indicator[dict[str, float | None]]):
    """Chandelier Exit

    Chandelier Exit places trailing stop levels below the rolling high and
    above the rolling low using an ATR multiple.

    Sources:
        https://chartschool.stockcharts.com/table-of-contents/technical-indicators-and-overlays/technical-overlays/chandelier-exit

    Output type: `Dict["long": float, "short": float]`

    Args:
        period (int): Lookback and ATR period. Defaults to 22.
        multiplier (float): ATR multiple. Defaults to 3.0.
    """

    _name: str = field(init=False, default="ChandelierExit")
    period: int = 22
    multiplier: float = 3.0

    def _generate_name(self) -> str:
        return f"{self._name}_{self.period}_{self.multiplier}"

    def _initialise(self):
        self.sub_atr = self.add_child(ATR(period=self.period))

    def _calculate_reading(self, index: int) -> dict[str, float | None]:
        atr_ = self.sub_atr.reading()
        if atr_ is None:
            return {"long": None, "short": None}

        high_ = highest(self.candles, "high", self.period, index)
        low_ = lowest(self.candles, "low", self.period, index)
        if high_ is None or low_ is None:
            return {"long": None, "short": None}

        atr_mult = self.multiplier * atr_
        return {
            "long": high_ - atr_mult,
            "short": low_ + atr_mult,
        }
