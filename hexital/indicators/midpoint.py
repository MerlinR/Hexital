from dataclasses import dataclass, field

from hexital.analysis.movement import highest, lowest
from hexital.core.indicator import Indicator


@dataclass(kw_only=True)
class MOP(Indicator):
    """Midpoint Over Period (MOP)

    A technical analysis tool that evaluates the average price movement by calculating the midpoint between the highest and lowest points over a specified period. This indicator aims to provide a smoother representation of price action, avoiding the choppiness of extreme highs and lows.
    """

    _name: str = field(init=False, default="MOP")
    period: int = 2
    input_value: str = "close"

    def _generate_name(self) -> str:
        return f"{self._name}_{self.period}"

    def _calculate_reading(self, index: int) -> float | dict | None:
        if self.prev_exists() or self.reading_period(self.period, self.input_value, index):
            return (
                lowest(self.candles, self.input_value, self.period, index)
                + highest(self.candles, self.input_value, self.period, index)
            ) * 0.5
        return None
