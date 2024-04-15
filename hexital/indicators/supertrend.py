from dataclasses import dataclass, field

from hexital import indicators
from hexital.core.indicator import Indicator, Managed


@dataclass(kw_only=True)
class Supertrend(Indicator):
    """Supertrend"""

    _name: str = field(init=False, default="Supertrend")
    period: int = 7
    multiplier: float = 3.0
    input_value: str = "close"

    def _generate_name(self) -> str:
        return f"{self._name}_{self.period}"

    def _initialise(self):
        self.add_sub_indicator(
            indicators.ATR(
                period=self.period,
                fullname_override=f"{self.name}_atr",
            )
        )
        self.add_sub_indicator(
            indicators.HighLowAverage(
                fullname_override=f"{self.name}_HL",
            )
        )
        self.add_managed_indicator("ST_data", Managed(fullname_override=f"{self.name}_data"))

    def _calculate_reading(self, index: int) -> float | dict | None:
        direction = 1
        trend = None
        long = None
        short = None

        if self.reading(f"{self.name}_atr"):
            mid_atr = self.multiplier * self.reading(f"{self.name}_atr")

            upper = self.reading(f"{self.name}_HL") + mid_atr
            lower = self.reading(f"{self.name}_HL") - mid_atr

            if self.prev_exists(f"{self.name}_data.lower"):
                if self.reading("close") > self.prev_reading(f"{self.name}_data.upper"):
                    direction = 1
                elif self.reading("close") < self.prev_reading(f"{self.name}_data.lower"):
                    direction = -1
                else:
                    direction = self.prev_reading(f"{self.name}.direction")
                    if direction == 1 and lower < self.prev_reading(f"{self.name}_data.lower"):
                        lower = self.prev_reading(f"{self.name}_data.lower")
                    if direction == -1 and upper > self.prev_reading(f"{self.name}_data.upper"):
                        upper = self.prev_reading(f"{self.name}_data.upper")

            self.managed_indicators["ST_data"].set_reading({"upper": upper, "lower": lower})

            trend = lower if direction == 1 else upper
            long = lower if direction == 1 else None
            short = upper if direction == -1 else None

        return {"trend": trend, "direction": direction, "long": long, "short": short}
