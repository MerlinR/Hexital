from dataclasses import dataclass, field

from hexital.core.indicator import Indicator
from hexital.indicators import EMA


@dataclass(kw_only=True)
class MACD(Indicator):
    """Moving Average Convergence Divergence (MACD)

    The MACD is a popular indicator to that is used to identify a security's trend.
    While APO and MACD are the same calculation, MACD also returns two more series
    called Signal and Histogram. The Signal is an EMA of MACD and the Histogram is
    the difference of MACD and Signal.

    Sources:
        https://www.investopedia.com/ask/answers/122314/what-exponential-moving-average-ema-formula-and-how-ema-calculated.asp

    Args:
        Input value (str): Default Close
        fast_period (int) Default: 12
        slow_period (int) Default: 26
        signal_period (int) Default: 19

    """

    _name: str = field(init=False, default="MACD")
    fast_period: int = 12
    slow_period: int = 26
    signal_period: int = 9
    input_value: str = "close"

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
        self._add_sub_indicator(
            EMA(
                input_value=self.input_value,
                period=self.fast_period,
                fullname_override=f"{self._name}_EMA_fast",
            )
        )
        self._add_sub_indicator(
            EMA(
                input_value=self.input_value,
                period=self.slow_period,
                fullname_override=f"{self._name}_EMA_slow",
            )
        )

        self._add_managed_indicator(
            "signal",
            EMA(
                input_value=f"{self.name}.MACD",
                period=self.signal_period,
                fullname_override=f"{self._name}_signal_line",
            ),
        )

    def _calculate_reading(self, index: int) -> float | dict | None:
        if self.reading(f"{self._name}_EMA_slow"):
            macd = self.reading(f"{self._name}_EMA_fast") - self.reading(f"{self._name}_EMA_slow")

            # Temp manually inserting MACD to be used by signal EMA calc
            self.candles[index].indicators[self.name] = {"MACD": macd}
            self._managed_indicators["signal"].calculate_index(index)

            signal = self._managed_indicators["signal"].reading()

            histogram = None
            if macd is not None and signal is not None:
                histogram = macd - signal

            return {"MACD": macd, "signal": signal, "histogram": histogram}

        return {"MACD": None, "signal": None, "histogram": None}
