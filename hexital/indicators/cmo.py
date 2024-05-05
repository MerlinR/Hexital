from dataclasses import dataclass, field

from hexital.core.indicator import Indicator, Managed


@dataclass(kw_only=True)
class CMO(Indicator):
    """Chande Momentum Oscillator - CMO

    https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/cmo
    """

    _name: str = field(init=False, default="CMO")
    period: int = 14
    input_value: str = "close"

    def _generate_name(self) -> str:
        return f"{self._name}_{self.period}"

    def _initialise(self):
        self.add_managed_indicator("RCO_data", Managed(fullname_override=f"{self.name}_data"))

    def _calculate_reading(self, index: int) -> float | dict | None:
        gains = None
        losses = None

        if self.prev_exists():
            change = self.prev_reading(self.input_value) - self.reading(self.input_value)

            change_gain = -1 * change if change < 0 else 0.0
            change_loss = change if change > 0 else 0.0

            gains = (
                (self.prev_reading(f"{self.name}_data.gain") * (self.period - 1)) + change_gain
            ) / self.period

            losses = (
                (self.prev_reading(f"{self.name}_data.loss") * (self.period - 1)) + change_loss
            ) / self.period

            self.managed_indicators["RCO_data"].set_reading({"gain": gains, "loss": losses})

        elif self.reading_period(self.period + 1, self.input_value):
            changes = [
                self.reading(self.input_value, i) - self.reading(self.input_value, i - 1)
                for i in range(index - (self.period - 1), index + 1)
            ]

            gains = sum(chng for chng in changes if chng > 0) / self.period
            losses = sum(abs(chng) for chng in changes if chng < 0) / self.period

            self.managed_indicators["RCO_data"].set_reading({"gain": gains, "loss": losses})

        if gains is not None and losses is not None:
            return ((gains - losses) / (gains + losses)) * 100

        self.managed_indicators["RCO_data"].set_reading(None)
        return None
