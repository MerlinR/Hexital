from dataclasses import dataclass, field

from hexital.core.indicator import Indicator


@dataclass(kw_only=True)
class EMA(Indicator):
    """Exponential Moving Average - EMA

    The Exponential Moving Average is more responsive moving average compared to the
    Simple Moving Average (SMA).  The weights are determined by alpha which is
    proportional to it's length.

    Sources:
        https://www.investopedia.com/ask/answers/122314/what-exponential-moving-average-ema-formula-and-how-ema-calculated.asp

    Output type: `float`

    Args:
        period (int): How many Periods to use. Defaults to 10
        source (str): Which input field to calculate the Indicator. Defaults to "close"
        smoothing (float): Smoothing multiplier for EMA. Defaults to 2.0
    """

    _name: str = field(init=False, default="EMA")
    period: int = 10
    source: str = "close"
    smoothing: float = 2.0
    _alpha: float = field(init=False, default=0)

    def _generate_name(self) -> str:
        return f"{self._name}_{self.period}"

    def _validate_fields(self):
        self._alpha = float(self.smoothing / (self.period + 1.0))

    def _calculate_reading(self, index: int) -> float | dict | None:
        prev_ema = self.prev_reading()
        if prev_ema is not None:
            return float(
                self._alpha * self.reading(self.source) + (prev_ema * (1.0 - self._alpha))
            )

        if self.reading_period(self.period, self.source):
            return self.candles_average(self.period, self.source)

        return None
