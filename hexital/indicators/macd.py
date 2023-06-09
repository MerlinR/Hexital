from dataclasses import dataclass

from hexital.indicators import EMA
from hexital.types import Indicator


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

    indicator_name: str = "MACD"
    input_value: str = "close"
    fast_period: int = 12
    slow_period: int = 26
    signal_period: int = 9

    def _generate_name(self) -> str:
        return "{}_{}_{}_{}".format(
            self.indicator_name, self.fast_period, self.slow_period, self.signal_period
        )

    def _initialise(self):
        self.add_sub_indicator(
            EMA(
                candles=self.candles,
                override_name=f"{self.indicator_name}_EMA_fast",
                period=self.fast_period,
            )
        )
        self.add_sub_indicator(
            EMA(
                candles=self.candles,
                override_name=f"{self.indicator_name}_EMA_slow",
                period=self.slow_period,
            )
        )

        self.add_managed_indicator(
            "signal_line",
            EMA(
                candles=self.candles,
                override_name=f"{self.indicator_name}_signal_line",
                period=self.signal_period,
                input_value=f"{self.name}.MACD",
            ),
        )

    def _calculate_new_reading(self, index: int = -1) -> float | dict | None:
        if all(
            [
                self.get_reading_by_index(index, sub_indicator)
                for sub_indicator in ["EMA_slow", "EMA_fast"]
            ]
        ):
            macd = self.get_reading_by_index(
                index, f"{self.indicator_name}_EMA_fast"
            ) - self.get_reading_by_index(index, f"{self.indicator_name}_EMA_slow")

            self.candles[index].indicators[self.name] = {"MACD": macd}
            self.get_managed_indictor("signal_line").calculate_index(index)

            signal = self.get_reading_by_index(index, "signal_line")

            histogram = None
            if macd is not None and signal is not None:
                histogram = macd - signal

            return {"MACD": macd, "signal": signal, "histogram": histogram}

        return None
