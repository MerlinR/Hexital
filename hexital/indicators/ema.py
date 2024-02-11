from dataclasses import dataclass, field

from hexital.core.indicator import Indicator


@dataclass(kw_only=True)
class EMA(Indicator):
    """Exponential Moving Average (EMA)

    The Exponential Moving Average is more responsive moving average compared to the
    Simple Moving Average (SMA).  The weights are determined by alpha which is
    proportional to it's length.

    Sources:
        https://www.investopedia.com/ask/answers/122314/what-exponential-moving-average-ema-formula-and-how-ema-calculated.asp

    Args:
        Input value (str): Default Close
        period (int) Default: 10

    """

    _name: str = field(init=False, default="EMA")
    input_value: str = "close"
    period: int = 10
    smoothing: float = 2.0

    def _generate_name(self) -> str:
        return f"{self._name}_{self.period}"

    def _calculate_reading(self, index: int) -> float | dict | None:
        if self.prev_exists():
            alpha = float(self.smoothing / (self.period + 1.0))
            return float(
                alpha * self.reading(self.input_value) + (self.prev_reading() * (1.0 - alpha))
            )

        if self.reading_period(self.period, self.input_value):
            return float(self.candles_sum(self.period, self.input_value) / self.period)

        return None
