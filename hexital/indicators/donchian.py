from dataclasses import dataclass, field

from ..analysis import movement
from ..core.indicator import Indicator


@dataclass(kw_only=True)
class Donchian(Indicator[dict[str, float | None]]):
    """Donchian Channels - Donchian

    Donchian Channels are a technical indicator that seeks to identify
    bullish and bearish extremes that favor reversals, higher and lower breakouts,
    breakdowns, and other emerging trends.

    Sources:
        https://upstox.com/learning-center/share-market/a-comprehensive-guide-to-donchian-channels-formula-calculation-and-strategic-uses/
        https://en.wikipedia.org/wiki/Donchian_channel

    Output type: `Dict["DCL": float, "DCM": float, "DCU": float]`

    Args:
        period (int): How many Periods to use. Defaults to 20
    """

    _name: str = field(init=False, default="DONCHIAN")
    period: int = 20

    def _calculate_reading(self, index: int) -> dict[str, float | None]:
        donchian: dict[str, float | None] = {"DCL": None, "DCM": None, "DCU": None}

        if self.prev_exists() or self.reading_period(self.period, "high", index):
            dcu = movement.highest(self.candles, "high", self.period - 1, index)
            dcl = movement.lowest(self.candles, "low", self.period - 1, index)
            dcm = (dcu + dcl) / 2
            donchian = {"DCL": dcl, "DCM": dcm, "DCU": dcu}

        return donchian
