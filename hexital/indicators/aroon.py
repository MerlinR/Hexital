from dataclasses import dataclass, field

from hexital.analysis import movement
from hexital.core.indicator import Indicator


@dataclass(kw_only=True)
class AROON(Indicator):
    """Aroon (aroon)
    Source: https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/aroon-indicator
    """

    _name: str = field(init=False, default="AROON")
    period: int = 14

    def _generate_name(self) -> str:
        return f"{self._name}_{self.period}"

    def _calculate_reading(self, index: int) -> float | dict | None:
        aroon = {
            "AROONU": None,
            "AROOND": None,
            "AROONOSC": None,
        }
        if self.reading_period(self.period + 1, "high"):
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
