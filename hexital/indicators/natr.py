from dataclasses import dataclass, field

from ..core.indicator import Indicator
from .atr import ATR


@dataclass(kw_only=True)
class NATR(Indicator[float | None]):
    """Normalized Average True Range - NATR

    NATR expresses ATR as a percentage of the current close, making volatility
    readings comparable across instruments with different price levels.

    Sources:
        https://tradingstrategy.ai/docs/api/technical-analysis/volatility/help/pandas_ta.volatility.natr.html

    Output type: `float`

    Args:
        period (int): How many periods to use. Defaults to 14.
    """

    _name: str = field(init=False, default="NATR")
    period: int = 14

    def _initialise(self):
        self.sub_atr = self.add_child(ATR(period=self.period))

    def _calculate_reading(self, index: int) -> float | None:
        atr = self.sub_atr.reading()
        close = self.close

        if atr is None or close == 0:
            return None

        return 100 * atr / close
