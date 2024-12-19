from dataclasses import dataclass, field

from hexital.analysis import movement
from hexital.core.indicator import Indicator


@dataclass(kw_only=True)
class AROON(Indicator):
    """Aroon - AROON

    The Aroon indicator, indicates if a price is trending or is in a trading range.
    It can also reveal the beginning of a new trend, its strength and can help anticipate
    changes from trading ranges to trends.

    Sources:
        https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/aroon-indicator


    Output type: `Dict["AROONU": float, "AROOND": float, "AROONOSC": float]`

    Args:
        period (int): How many Periods to use. Defaults to 14
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
        if self.prev_exists() or self.reading_period(self.period + 1, "high"):
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
