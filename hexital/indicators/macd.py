from dataclasses import dataclass, field

from hexital.core.indicator import Indicator, Managed
from hexital.indicators import EMA


@dataclass(kw_only=True)
class MACD(Indicator):
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
    source: str = "close"
    fast_period: int = 12
    slow_period: int = 26
    signal_period: int = 9

    def _generate_name(self) -> str:
        return "{}_{}_{}_{}".format(
            self._name,
            self.fast_period,
            self.slow_period,
            self.signal_period,
        )

    def _validate_fields(self):
        if self.slow_period < self.fast_period:
            self.fast_period, self.slow_period = self.slow_period, self.fast_period

    def _initialise(self):
        self.add_managed_indicator("MACD", Managed(name=f"{self.name}_macd"))

        self.add_sub_indicator(
            EMA(
                source=self.source,
                period=self.fast_period,
                name=f"{self.name}_EMA_fast",
            )
        )
        self.add_sub_indicator(
            EMA(
                source=self.source,
                period=self.slow_period,
                name=f"{self.name}_EMA_slow",
            )
        )
        self.add_managed_indicator(
            "signal",
            EMA(
                source=f"{self.name}_macd",
                period=self.signal_period,
                name=f"{self.name}_signal_line",
            ),
        )

    def _calculate_reading(self, index: int) -> float | dict | None:
        ema_slow = self.reading(f"{self.name}_EMA_slow")

        if ema_slow is not None:
            macd = self.reading(f"{self.name}_EMA_fast") - ema_slow

            self.managed_indicators["MACD"].set_reading(macd)
            self.managed_indicators["signal"].calculate_index(index)
            signal = self.managed_indicators["signal"].reading()

            if signal is not None:
                histogram = macd - signal
                return {"MACD": macd, "signal": signal, "histogram": histogram}

        return {"MACD": None, "signal": None, "histogram": None}
