from dataclasses import dataclass, field

from ..core.indicator import Indicator, Source
from .hlca import HLCA
from .sma import SMA


@dataclass(kw_only=True)
class CCI(Indicator[float | None]):
    """Commodity Channel Index - CCI

    The Commodity Channel Index measures the current typical price relative to
    its rolling mean and mean absolute deviation over a fixed lookback period.
    It is commonly used to identify overbought, oversold, and trend deviation
    conditions.

    Output type: `float`

    Args:
        period (int): How many periods to use. Defaults to 14
        source (str): Which input field to calculate the indicator from.
            Defaults to `"close"`
        c (float): Constant scaling factor applied to the mean absolute
            deviation. Defaults to 0.015
    """

    _name: str = field(init=False, default="CCI")
    period: int = 14
    source: Source = "close"
    scaling: float = 0.015

    def _name_parts(self) -> list[str]:
        return ["period", "scaling", "source"]

    def _initialise(self):
        self.sub_hlca = self.add_child(HLCA(name=f"{self.name}_hlca"))
        self.sub_sma = self.add_child(
            SMA(name=f"{self.name}_sma", source=self.sub_hlca, period=self.period)
        )

    def _calculate_reading(self, index: int) -> float | None:
        typical_price = self.sub_hlca.reading()
        mean_typical_price = self.sub_sma.reading()

        if typical_price is None or mean_typical_price is None:
            return None

        if not self.sub_hlca.reading_period(self.period, index=index):
            return None

        mean_deviation = (
            sum(
                abs(self.sub_hlca.reading(index=index - offset) - mean_typical_price)
                for offset in range(self.period)
            )
            / self.period
        )

        if mean_deviation == 0:
            return None

        return (typical_price - mean_typical_price) / (self.scaling * mean_deviation)
