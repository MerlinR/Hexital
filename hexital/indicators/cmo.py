from dataclasses import dataclass, field

from ..core.indicator import Indicator, Source


@dataclass(kw_only=True)
class CMO(Indicator[float | None]):
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
    source: Source = "close"

    def _minimum_candles(self) -> int:
        return self.period + 1

    def _initialise(self):
        self._state = self.add_state()

    def _calculate_reading(self, index: int) -> float | None:
        gains = None
        losses = None

        if self.prev_exists():
            change = self.prev_src() - self.src()

            change_gain = -1 * change if change < 0 else 0.0
            change_loss = change if change > 0 else 0.0

            gains = (
                (self._state.prev("gain") * (self.period - 1)) + change_gain
            ) / self.period

            losses = (
                (self._state.prev("loss") * (self.period - 1)) + change_loss
            ) / self.period

        elif self.reading_period(self.period + 1, self.source):
            changes = [
                self.at_src(i) - self.at_src(i - 1)
                for i in range(index - (self.period - 1), index + 1)
            ]

            gains = sum(chng for chng in changes if chng > 0) / self.period
            losses = sum(abs(chng) for chng in changes if chng < 0) / self.period

        self._state.update(gain=gains, loss=losses)

        if gains is None or losses is None:
            return None

        momentum = gains + losses
        if momentum == 0:
            return 0.0

        return ((gains - losses) / momentum) * 100
