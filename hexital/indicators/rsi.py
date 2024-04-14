from dataclasses import dataclass, field

from hexital.core.indicator import Indicator, Managed


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

    _name: str = field(init=False, default="RSI")
    period: int = 14
    input_value: str = "close"

    def _generate_name(self) -> str:
        return f"{self._name}_{self.period}"

    def _initialise(self):
        self.add_managed_indicator("RSI_data", Managed(fullname_override=f"{self.name}_data"))

    def _calculate_reading(self, index: int) -> float | dict | None:
        if self.prev_exists():
            change = self.prev_reading(self.input_value) - self.reading(self.input_value)

            change_gain = -1 * change if change < 0 else 0.0
            change_loss = change if change > 0 else 0.0

            self.managed_indicators["RSI_data"].set_reading(
                {
                    "gain": (
                        (self.prev_reading(f"{self.name}_data.gain") * (self.period - 1))
                        + change_gain
                    )
                    / self.period,
                    "loss": (
                        (self.prev_reading(f"{self.name}_data.loss") * (self.period - 1))
                        + change_loss
                    )
                    / self.period,
                }
            )

        elif self.reading_period(self.period + 1, self.input_value):
            changes = [
                self.reading(self.input_value, i) - self.reading(self.input_value, i - 1)
                for i in range(index - (self.period - 1), index + 1)
            ]
            self.managed_indicators["RSI_data"].set_reading(
                {
                    "gain": sum(chng for chng in changes if chng > 0) / self.period,
                    "loss": sum(abs(chng) for chng in changes if chng < 0) / self.period,
                }
            )

        if self.reading(f"{self.name}_data"):
            rs = self.reading(f"{self.name}_data.gain") / self.reading(f"{self.name}_data.loss")
            rsi = 100.0 - (100.0 / (1.0 + rs))
            return rsi

        self.managed_indicators["RSI_data"].set_reading(None)
        return None
