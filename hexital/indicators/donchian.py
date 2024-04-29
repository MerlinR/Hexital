from dataclasses import dataclass, field

from hexital.analysis import movement
from hexital.core.indicator import Indicator


@dataclass(kw_only=True)
class Donchian(Indicator):
    """Donchian Channels: (donchian)


    Sources:
        https://upstox.com/learning-center/share-market/a-comprehensive-guide-to-donchian-channels-formula-calculation-and-strategic-uses/

    Args:
        Input value (str): Default Close
        period (int) Default: 20


    """

    _name: str = field(init=False, default="DONCHIAN")
    period: int = 20

    def _generate_name(self) -> str:
        return f"{self._name}_{self.period}"

    def _calculate_reading(self, index: int) -> float | dict | None:
        donchian = {"DCL": None, "DCM": None, "DCU": None}

        if self.prev_reading(f"{self.name}.DCU") is not None or self.reading_period(
            self.period, "high", index
        ):
            donchian["DCU"] = movement.highest(self.candles, "high", self.period - 1, index)
            donchian["DCL"] = movement.lowest(self.candles, "low", self.period - 1, index)
            donchian["DCM"] = (donchian["DCU"] + donchian["DCL"]) / 2

        return donchian
