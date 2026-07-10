from dataclasses import dataclass, field

from ..core.indicator import Indicator, Source
from .sma import SMA
from .stdev import STDEV


@dataclass(kw_only=True)
class BBANDS(Indicator[dict[str, float | None]]):
    """Bollinger Bands - BBANDS

    Bollinger Bands are a type of statistical chart characterizing
    the prices and volatility over time of a financial instrument or commodity,
    using a formulaic method.

    Sources:
        https://www.britannica.com/money/bollinger-bands-indicator

    Output type: `Dict["BBL": float, "BBM": float, "BBU": float]`

    Args:
        period (int): How many Periods to use. Defaults to 5
        source (str): Which input field to calculate the Indicator. Defaults to "close"
    """

    _name: str = field(init=False, default="BBANDS")
    period: int = 5
    source: Source = "close"
    std: float = 2.0

    def _initialise(self):
        self.sub_stdev = self.add_child(STDEV(source=self.source, period=self.period))
        self.sub_sma = self.add_child(SMA(source=self.source, period=self.period))

    def _calculate_reading(self, index: int) -> dict[str, float | None]:
        bbands = {"BBL": None, "BBM": None, "BBU": None}

        if self.prev_exists() or (self.sub_sma.exists() and self.sub_stdev.exists()):
            sma = self.sub_sma.reading()
            stdev = self.sub_stdev.reading()

            bbands = {
                "BBM": sma,
                "BBL": sma - (stdev * self.std),
                "BBU": sma + (stdev * self.std),
            }

        return bbands
