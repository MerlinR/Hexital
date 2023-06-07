from dataclasses import dataclass

from hexital.indicators import Managed
from hexital.types import Indicator


@dataclass(kw_only=True)
class RSI(Indicator):
    """Relative Strength Index (RSI)

    The Relative Strength Index is popular momentum oscillator used to measure the
    velocity as well as the magnitude of directional price movements.

    Sources:
        https://www.tradingview.com/support/solutions/43000502338-relative-strength-index-rsi/

    Args:
        Input value (str): Default Close
        period (int) Default: 14


    """

    indicator_name: str = "RSI"
    input_value: str = "close"
    period: int = 14

    def _generate_name(self) -> str:
        return f"{self.indicator_name}_{self.period}"

    def _initialise(self):
        self.add_managed_indicator(
            "RSI_avg_gain", Managed(candles=self.candles, name_postfix="RSI_avg_gain")
        )
        self.add_managed_indicator(
            "RSI_avg_loss", Managed(candles=self.candles, name_postfix="RSI_avg_loss")
        )

    def _calculate_new_value(self, index: int = -1) -> float | dict | None:
        if self.get_indicator_by_index(index - 1, "RSI_avg_gain"):
            diff = self.get_indicator_by_index(
                index - 1, self.input_value
            ) - self.get_indicator_by_index(index, self.input_value)

            self.get_managed_indictor("RSI_avg_gain").set_value(
                index,
                (
                    (
                        self.get_indicator_by_index(index - 1, "RSI_avg_gain")
                        * (self.period - 1)
                    )
                    + (diff * -1 if diff < 0 else 0)
                )
                / self.period,
            )
            self.get_managed_indictor("RSI_avg_loss").set_value(
                index,
                (
                    (
                        self.get_indicator_by_index(index - 1, "RSI_avg_loss")
                        * (self.period - 1)
                    )
                    + (diff if diff > 0 else 0)
                )
                / self.period,
            )
            if self.get_indicator_by_index(index) == 0:
                return 100.0

            rs = self.get_indicator_by_index(
                index, "RSI_avg_gain"
            ) / self.get_indicator_by_index(index, "RSI_avg_loss")

            rsi = 100.0 - (100.0 / (1.0 + rs))

            return rsi

        if self.get_indicator_period(self.period, index, self.input_value):
            diffs = [
                self.get_indicator_by_index(i - 1, self.input_value)
                - self.get_indicator_by_index(i, self.input_value)
                for i in range(index - (self.period - 1), index + 1)
            ]
            self.get_managed_indictor("RSI_avg_gain").set_value(
                index,
                sum(diff * -1 if diff < 0 else 0 for diff in diffs) / self.period,
            )
            self.get_managed_indictor("RSI_avg_loss").set_value(
                index,
                sum(diff if diff > 0 else 0 for diff in diffs) / self.period,
            )

        return None
