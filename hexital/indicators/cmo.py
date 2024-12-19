from dataclasses import dataclass, field

from hexital.core.indicator import Indicator, Managed


@dataclass(kw_only=True)
class CMO(Indicator):
    """Chande Momentum Oscillator - CMO

    The CMO indicator is created by calculating the difference between the
    sum of all recent higher closes and the sum of all recent lower closes
    and then dividing the result by the sum of all price movement over a given time period.
    The result is multiplied by 100 to give the -100 to +100 range.

    Sources:
        https://www.fidelity.com/learning-center/trading-investing/technical-analysis/technical-indicator-guide/cmo

    Output type: `float`

    Args:
        period (int): How many Periods to use. Defaults to 14
        source (str): Which input field to calculate the Indicator. Defaults to "close"
    """

    _name: str = field(init=False, default="CMO")
    period: int = 14
    source: str = "close"

    def _generate_name(self) -> str:
        return f"{self._name}_{self.period}"

    def _initialise(self):
        self.add_managed_indicator("data", Managed(name=f"{self.name}_data"))

    def _calculate_reading(self, index: int) -> float | dict | None:
        gains = None
        losses = None

        if self.prev_exists():
            change = self.prev_reading(self.source) - self.reading(self.source)

            change_gain = -1 * change if change < 0 else 0.0
            change_loss = change if change > 0 else 0.0

            gains = (
                (self.prev_reading(f"{self.name}_data.gain") * (self.period - 1)) + change_gain
            ) / self.period

            losses = (
                (self.prev_reading(f"{self.name}_data.loss") * (self.period - 1)) + change_loss
            ) / self.period

        elif self.reading_period(self.period + 1, self.source):
            changes = [
                self.reading(self.source, i) - self.reading(self.source, i - 1)
                for i in range(index - (self.period - 1), index + 1)
            ]

            gains = sum(chng for chng in changes if chng > 0) / self.period
            losses = sum(abs(chng) for chng in changes if chng < 0) / self.period

        self.managed_indicators["data"].set_reading({"gain": gains, "loss": losses})

        if gains is not None and losses is not None:
            return ((gains - losses) / (gains + losses)) * 100
