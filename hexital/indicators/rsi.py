from dataclasses import dataclass

from hexital.indicators import Managed
from hexital.types import Indicator


@dataclass()
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
            "RSI_gain",
            Managed(indicator_name="RSI_gain", candles=self.candles),
        )
        self.add_managed_indicator(
            "RSI_loss",
            Managed(indicator_name="RSI_loss", candles=self.candles),
        )

    def _calculate_reading(self, index: int = -1) -> float | dict | None:
        if self.prev_exists(index):
            change = self.reading_by_index(
                index - 1, self.input_value
            ) - self.reading_by_index(index, self.input_value)

            change_gain = -1 * change if change < 0 else 0.0
            change_loss = change if change > 0 else 0.0

            self.managed_indictor("RSI_gain").set_reading(
                index,
                (
                    (self.reading_by_index(index - 1, "RSI_gain") * (self.period - 1))
                    + change_gain
                )
                / self.period,
            )
            self.managed_indictor("RSI_loss").set_reading(
                index,
                (
                    (self.reading_by_index(index - 1, "RSI_loss") * (self.period - 1))
                    + change_loss
                )
                / self.period,
            )
        elif self.reading_period(self.period + 1, index=index, name=self.input_value):
            changes = [
                self.reading_by_index(i, self.input_value)
                - self.reading_by_index(i - 1, self.input_value)
                for i in range(index - (self.period - 1), index + 1)
            ]
            self.managed_indictor("RSI_gain").set_reading(
                index,
                sum(chng for chng in changes if chng > 0) / self.period,
            )
            self.managed_indictor("RSI_loss").set_reading(
                index,
                sum(-1 * chng for chng in changes if chng < 0) / self.period,
            )

        if self.reading_by_index(index, "RSI_gain"):
            rs = self.reading_by_index(index, "RSI_gain") / self.reading_by_index(
                index, "RSI_loss"
            )
            rsi = 100.0 - (100.0 / (1.0 + rs))
            return rsi

        self.managed_indictor("RSI_gain").set_reading(index, None)
        self.managed_indictor("RSI_loss").set_reading(index, None)
        return None
