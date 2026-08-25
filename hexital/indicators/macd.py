from dataclasses import dataclass, field

from ..core.indicator import Indicator, Source
from .ema import EMA


@dataclass(kw_only=True)
class MACD(Indicator[dict[str, float | None]]):
    """Moving Average Convergence Divergence - MACD

    The MACD is a popular indicator to that is used to identify a security's trend.
    While APO and MACD are the same calculation, MACD also returns two more series
    called Signal and Histogram. The Signal is an EMA of MACD and the Histogram is
    the difference of MACD and Signal.

    Sources:
        https://www.investopedia.com/ask/answers/122314/what-exponential-moving-average-ema-formula-and-how-ema-calculated.asp

    Output type: `Dict["MACD": float, "signal": float, "histogram": float]`

    Args:
        source (str): Which input field to calculate the Indicator. Defaults to "close"
        fast_period (int): How many Periods to use for fast EMA. Defaults to 12
        slow_period (int): How many Periods to use for slow EMA. Defaults to 26
        signal_period (int): How many Periods to use for MACD signal. Defaults to 9
    """

    _name: str = field(init=False, default="MACD")
    source: Source = "close"
    fast_period: int = 12
    slow_period: int = 26
    signal_period: int = 9

    def _name_parts(self) -> list[str]:
        return ["fast_period", "slow_period", "signal_period", "source"]

    def _validate_fields(self):
        if self.slow_period < self.fast_period:
            self.fast_period, self.slow_period = self.slow_period, self.fast_period

    def _minimum_candles(self) -> int:
        return self.slow_period + self.signal_period - 1

    def _initialise(self):
        self._macd = self.add_state(name=f"{self.name}_macd")

        self.sub_emaf = self.add_child(EMA(source=self.source, period=self.fast_period))
        self.sub_emas = self.add_child(EMA(source=self.source, period=self.slow_period))
        self.sub_signal = self.add_child_managed(
            EMA(source=self._macd.managed, period=self.signal_period),
        )

    def _calculate_reading(self, index: int) -> dict[str, float | None]:
        ema_slow = self.sub_emas.reading()

        if ema_slow is None:
            return {"MACD": None, "signal": None, "histogram": None}

        macd = self.sub_emaf.reading() - ema_slow

        self._macd.set(macd)
        self.sub_signal.calculate_index(index)

        signal = self.sub_signal.reading()

        if signal is not None:
            histogram = macd - signal
            return {"MACD": macd, "signal": signal, "histogram": histogram}

        return {"MACD": None, "signal": None, "histogram": None}
