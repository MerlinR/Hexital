from dataclasses import dataclass

from hexital import indicators
from hexital.core import Indicator


@dataclass(kw_only=True)
class Supertrend(Indicator):
    """Supertrend"""

    indicator_name: str = "Supertrend"
    period: int = 7
    mulitplier: float = 3.0
    input_value: str = "close"

    def _generate_name(self) -> str:
        return f"{self.indicator_name}_{self.period}"

    def _initialise(self):
        self._add_sub_indicator(
            indicators.ATR(
                candles=self.candles,
                period=self.period,
                fullname_override=f"{self.indicator_name}_atr",
            )
        )
        self._add_sub_indicator(
            indicators.HighLowAverage(
                candles=self.candles,
                fullname_override=f"{self.indicator_name}_HL",
            )
        )

        self._add_managed_indicator(
            "basic_upper",
            indicators.Managed(
                candles=self.candles,
                fullname_override="ST_Upper",
            ),
        )
        self._add_managed_indicator(
            "basic_lower",
            indicators.Managed(
                candles=self.candles,
                fullname_override="ST_Lower",
            ),
        )

    def _calculate_reading(self, index: int) -> float | dict | None:
        direction = 1
        trend = None

        if self.reading(f"{self.indicator_name}_atr"):
            matr = self.mulitplier * self.reading(f"{self.indicator_name}_atr")

            upper = self.reading(f"{self.indicator_name}_HL") + matr
            lower = self.reading(f"{self.indicator_name}_HL") - matr

            if self.prev_reading(f"{self.name}.long"):
                if self.reading("close") > self.prev_reading("ST_Upper"):
                    direction = 1
                elif self.reading("close") < self.prev_reading("ST_Lower"):
                    direction = -1
                else:
                    direction = self.prev_reading(f"{self.name}.direction")
                    if direction > 0 and lower < self.prev_reading("ST_Lower"):
                        lower = self.prev_reading("ST_Lower")
                    if direction < 0 and upper > self.prev_reading("ST_Upper"):
                        upper = self.prev_reading("ST_Upper")

            self._managed_indictor("basic_upper").set_reading(upper)
            self._managed_indictor("basic_lower").set_reading(lower)

            return {
                "trend": lower if direction == 1 else upper,
                "direction": direction,
                "long": lower if direction == 1 else None,
                "short": upper if direction == -1 else None,
            }

        return {"trend": trend, "direction": direction, "long": None, "short": None}
