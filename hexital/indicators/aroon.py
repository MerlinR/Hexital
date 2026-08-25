from dataclasses import dataclass, field
from typing import cast

from ..analysis import movement
from ..core.indicator import Indicator


@dataclass(kw_only=True)
class AROON(Indicator[dict[str, float | None]]):
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

    def _minimum_candles(self) -> int:
        return self.period + 1

    def _calculate_reading(self, index: int) -> dict[str, float | None]:
        aroon: dict[str, float | None] = {
            "AROONU": None,
            "AROOND": None,
            "AROONOSC": None,
        }

        if self.prev_exists() or self.reading_period(self.period + 1, "high"):
            aroon["AROONU"] = (
                (
                    self.period
                    - cast(
                        float,
                        movement.highestbar(self.candles, "high", self.period + 1, index),
                    )
                )
                / self.period
            ) * 100
            aroon["AROOND"] = (
                (
                    self.period
                    - cast(
                        float,
                        movement.lowestbar(self.candles, "low", self.period + 1, index),
                    )
                )
                / self.period
            ) * 100

            aroon["AROONOSC"] = aroon["AROONU"] - aroon["AROOND"]

        return aroon
