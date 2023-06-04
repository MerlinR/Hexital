from dataclasses import dataclass

from hexital.types import Indicator


@dataclass(kw_only=True)
class EMA(Indicator):
    """Exponential Moving Average (EMA)

    The Exponential Moving Average is more responsive moving average compared to the
    Simple Moving Average (SMA).  The weights are determined by alpha which is
    proportional to it's length.

    Sources:
        https://www.investopedia.com/ask/answers/122314/what-exponential-moving-average-ema-formula-and-how-ema-calculated.asp

    Args:
        period (int) Default: 10
        Input value (str): Default Close
    """

    indicator_name: str = "EMA"
    period: int = 10
    input_value: str = "close"
    multiplier: float = 2.0

    def _generate_name(self) -> str:
        return f"{self.indicator_name}_{self.period}"

    def _calculate_new_value(self, index: int = -1) -> float | dict | None:
        if self.get_indicator_by_index(index - 1) is not None:
            mult = self.multiplier / (self.period + 1.0)
            return float(
                mult * self.get_indicator_by_index(index, self.input_value)
                + (1.0 - mult) * self.get_indicator_by_index(index - 1)
            )

        if self.get_indicator_period(self.period - 1, index, self.input_value):
            return (
                sum(
                    self.get_indicator_by_candle(value, self.input_value)
                    for value in self.candles[index - (self.period - 1) : index + 1]
                )
                / self.period
            )

        return None
