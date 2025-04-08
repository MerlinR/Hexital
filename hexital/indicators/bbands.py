from dataclasses import dataclass, field

from hexital.core.indicator import Indicator, Source
from hexital.indicators.sma import SMA
from hexital.indicators.stdev import STDEV


@dataclass(kw_only=True)
class BBANDS(Indicator[dict]):
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
    _std: float = field(init=False, default=2.0)

    def _generate_name(self) -> str:
        return f"{self._name}_{self.period}"

    def _initialise(self):
        self.sub_stdev = self.add_sub_indicator(STDEV(source=self.source, period=self.period))
        self.sub_sma = self.add_sub_indicator(SMA(source=self.source, period=self.period))

    def _calculate_reading(self, index: int) -> dict:
        bbands = {
            "BBL": None,
            "BBM": None,
            "BBU": None,
        }
        if self.prev_exists() or (self.sub_sma.exists() and self.sub_stdev.exists()):
            sma = self.sub_sma.reading()
            stdev = self.sub_stdev.reading()

            bbands = {
                "BBM": sma,
                "BBL": sma - (stdev * self._std),
                "BBU": sma + (stdev * self._std),
            }

        return bbands
