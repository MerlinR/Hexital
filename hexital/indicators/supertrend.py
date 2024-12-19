from dataclasses import dataclass, field

from hexital import indicators
from hexital.core.indicator import Indicator, Managed


@dataclass(kw_only=True)
class Supertrend(Indicator):
    """Supertrend

    It is used to identify market trends and potential entry and exit points in trading.
    The indicator is based on two dynamic values, period and multiplier, and incorporates
    the concept of Average True Range (ATR) to measure market volatility.
    The SuperTrend Indicator generates buy and sell signals by plotting a line on the price chart.

    Output type: `Dict["trend": float, "direction": int, "short": float]`

    Args:
        period (int): How many Periods to use. Defaults to 7
        source (str): Which input field to calculate the Indicator. Defaults to "close"
        multiplier (float): A positive float to multiply the ATR. Defaults to 3.0
    """

    _name: str = field(init=False, default="Supertrend")
    period: int = 7
    source: str = "close"
    multiplier: float = 3.0

    def _generate_name(self) -> str:
        return f"{self._name}_{self.period}"

    def _initialise(self):
        self.add_sub_indicator(indicators.ATR(period=self.period, name=f"{self.name}_atr"))
        self.add_sub_indicator(indicators.HLA(name=f"{self.name}_HL"))
        self.add_managed_indicator("data", Managed(name=f"{self.name}_data"))

    def _calculate_reading(self, index: int) -> float | dict | None:
        direction = 1
        trend = None
        long = None
        short = None

        atr_ = self.reading(f"{self.name}_atr")

        if atr_ is not None:
            mid_atr = self.multiplier * atr_

            upper = self.reading(f"{self.name}_HL") + mid_atr
            lower = self.reading(f"{self.name}_HL") - mid_atr

            prev_upper = self.prev_reading(f"{self.name}_data.upper")
            prev_lower = self.prev_reading(f"{self.name}_data.lower")

            if self.prev_exists(f"{self.name}_data.lower"):
                if self.candles[index].close > prev_upper:
                    direction = 1
                elif self.candles[index].close < prev_lower:
                    direction = -1
                else:
                    direction = self.prev_reading(f"{self.name}.direction")
                    if direction == 1 and lower < prev_lower:
                        lower = prev_lower
                    if direction == -1 and upper > prev_upper:
                        upper = prev_upper

            self.managed_indicators["data"].set_reading({"upper": upper, "lower": lower})

            trend = lower if direction == 1 else upper
            long = lower if direction == 1 else None
            short = upper if direction == -1 else None

        return {"trend": trend, "direction": direction, "long": long, "short": short}
