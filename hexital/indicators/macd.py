from dataclasses import dataclass

from hexital.indicators.ema import EMA
from hexital.types import Indicator

# Issues
#
# 1: get_indicator does not work with nested dict indicators
#
# 2: sub_indicators that require part of current indicator


@dataclass(kw_only=True)
class MACD(Indicator):
    indicator_name: str = "MACD"
    fast_period: int = 12
    slow_period: int = 26
    signal_period: int = 9
    input_value: str = "close"

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

    def _calculate_new_value(self, index: int = -1) -> float | dict | None:
        if all(
            [
                self.get_indicator(self.candles[index], sub_indicator)
                for sub_indicator in ["EMA_slow", "EMA_fast"]
            ]
        ):
            macd = self.get_indicator(
                self.candles[index], f"{self.indicator_name}_EMA_fast"
            ) - self.get_indicator(self.candles[index], f"{self.indicator_name}_EMA_slow")

            self.candles[index].indicators[self.name] = {"MACD": macd}
            self.get_managed_indictor("signal_line").calculate_index(index)

            signal = self.get_indicator(self.candles[index], "signal_line")

            histogram = None
            if macd is not None and signal is not None:
                histogram = macd - signal

            return {"MACD": macd, "signal": signal, "histogram": histogram}

        return None
