from dataclasses import dataclass, field

from hexital.core.indicator import Indicator
from hexital.indicators.sma import SMA
from hexital.indicators.stdev import StandardDeviation


@dataclass(kw_only=True)
class BBANDS(Indicator):
    """Bollinger Bands (BBANDS)
    Source: https://www.britannica.com/money/bollinger-bands-indicator
    """

    _name: str = field(init=False, default="BBANDS")
    period: int = 5
    input_value: str = "close"
    _std: float = field(init=False, default=2.0)

    def _generate_name(self) -> str:
        return f"{self._name}_{self.period}"

    def _initialise(self):
        self.add_sub_indicator(StandardDeviation(input_value=self.input_value, period=self.period))
        self.add_sub_indicator(SMA(input_value=self.input_value, period=self.period))

    def _calculate_reading(self, index: int) -> float | dict | None:
        bbands = {
            "BBL": None,
            "BBM": None,
            "BBU": None,
        }
        if (
            self.reading(f"SMA_{self.period}") is not None
            and self.reading(f"STDEV_{self.period}") is not None
        ):
            sma = self.reading(f"SMA_{self.period}")
            stdev = self.reading(f"STDEV_{self.period}")

            bbands["BBM"] = sma
            bbands["BBL"] = sma - (stdev * self._std)
            bbands["BBU"] = sma + (stdev * self._std)

        return bbands
