from dataclasses import dataclass, field

from ..analysis.utils import highest, lowest
from ..core.indicator import Indicator


@dataclass(kw_only=True)
class Ichimoku(Indicator[dict[str, float | None]]):
    """Ichimoku Kinko Hyo - ICHIMOKU

    Ichimoku is a multi-line trend indicator composed of a conversion line,
    base line, two leading spans, and an optional chikou span.

    This implementation is incremental and does not require future candle data.
    Shifted components are written to their target candle indexes as new candles
    arrive, so the chikou span updates older candle readings in place.

    Output type: `Dict["Lead_A": float, "Lead_B": float, "Conversion": float, "Base": float, "Span": float]`

    Args:
        tenkan (int): Tenkan period. Defaults to 9
        kijun (int): Kijun period. Defaults to 26
        senkou (int): Senkou period. Defaults to 52
        include_chikou (bool): Include the chikou span. Defaults to True
        offset (int): Post shift. Defaults to 0
    """

    _name: str = field(init=False, default="ICHIMOKU")
    tenkan: int = 9
    kijun: int = 26
    senkou: int = 52
    include_chikou: bool = True
    offset: int = 0

    def _generate_name(self) -> str:
        return f"{self._name}_{self.tenkan}_{self.kijun}_{self.senkou}"

    def _initialise(self):
        self._shifted = self.add_state(name=f"{self.name}_shifted")

    def _midprice(self, period: int, index: int) -> float | None:
        if not self.reading_period(period, "high", index):
            return None

        high_ = highest(self.candles, "high", period, index)
        low_ = lowest(self.candles, "low", period, index)

        if high_ is None or low_ is None:
            return None

        return (high_ + low_) * 0.5

    def _calculate_reading(self, index: int) -> dict[str, float | None]:
        conversion = self._midprice(self.tenkan, index)
        base = self._midprice(self.kijun, index)
        lead_b_source = self._midprice(self.senkou, index)

        lead_a_source = None
        if conversion is not None and base is not None:
            lead_a_source = (conversion + base) * 0.5

        lead_index = index + self.kijun + self.offset
        if lead_index < len(self.candles):
            self._shifted.update(lead_index, lead_a=lead_a_source, lead_b=lead_b_source)

        if self.include_chikou:
            target_index = index - self.kijun + self.offset
            if 0 <= target_index < len(self.candles):
                self._shifted.update(target_index, span=self.close)
                target_reading = self.reading(
                    index=target_index,
                    default={
                        "Lead_A": None,
                        "Lead_B": None,
                        "Conversion": None,
                        "Base": None,
                        "Span": None,
                    },
                )
                target_reading["Span"] = self.close
                self._set_reading(target_reading, index=target_index)

        return {
            "Lead_A": self.reading(self._shifted.source("lead_a")),
            "Lead_B": self.reading(self._shifted.source("lead_b")),
            "Conversion": conversion,
            "Base": base,
            "Span": self.reading(self._shifted.source("span"))
            if self.include_chikou
            else None,
        }
