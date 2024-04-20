from dataclasses import dataclass, field

from hexital.analysis import movement
from hexital.core.indicator import Indicator
from hexital.indicators.sma import SMA
from hexital.indicators.stdev import STDEV


@dataclass(kw_only=True)
class AROON(Indicator):
    """Aroon (aroon)
    Source: https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/aroon-indicator
    """

    _name: str = field(init=False, default="AROON")
    period: int = 14
    input_value: str = "close"

    def _generate_name(self) -> str:
        return f"{self._name}_{self.period}"

    def _initialise(self):
        self.add_sub_indicator(STDEV(period=self.period))
        self.add_sub_indicator(SMA(period=self.period))

    def _calculate_reading(self, index: int) -> float | dict | None:
        aroon = {
            "AROONU": None,
            "AROOND": None,
            "AROONOSC": None,
        }
        if self.reading_period(self.period + 1, self.input_value):
            aroon["AROONU"] = (
                (self.period - movement.highestbar(self.candles, "high", self.period + 1, index))
                / self.period
            ) * 100
            aroon["AROOND"] = (
                (self.period - movement.lowestbar(self.candles, "low", self.period + 1, index))
                / self.period
            ) * 100

            aroon["AROONOSC"] = aroon["AROONU"] - aroon["AROOND"]

        return aroon
