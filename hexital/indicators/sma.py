from dataclasses import dataclass, field

from ..core.indicator import Indicator, Source


@dataclass(kw_only=True)
class SMA(Indicator[float | None]):
    """Simple Moving Average - SMA

    The Simple Moving Average is the classic moving average that is the equally
    weighted average over n periods.

    Sources:
        https://www.investopedia.com/terms/s/sma.asp

    Output type: `float`

    Args:
        period (int): How many Periods to use. Defaults to 10
        source (str): Which input field to calculate the Indicator. Defaults to "close"
    """

    _name: str = field(init=False, default="SMA")
    period: int = 10
    source: Source = "close"

    def _generate_name(self) -> str:
        return f"{self._name}_{self.period}"

    def _calculate_reading(self, index: int) -> float | None:
        if self.prev_exists():
            prev = self.prev()
            old = self.at_src(index - self.period)
            new = self.src()
            if prev is not None and old is not None and new is not None:
                return prev - (old - new) / self.period
            return None

        if self.reading_period(self.period, self.source):
            return self.candles_average(self.period, self.source)

        return None
