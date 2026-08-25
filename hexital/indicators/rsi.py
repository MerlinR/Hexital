from dataclasses import dataclass, field

from ..core.indicator import Indicator, Source


@dataclass(kw_only=True)
class RSI(Indicator[float | None]):
    """Relative Strength Index - RSI

    The Relative Strength Index is popular momentum oscillator used to measure the
    velocity as well as the magnitude of directional price movements.

    Sources:
        https://www.tradingview.com/support/solutions/43000502338-relative-strength-index-rsi/

    Output type: `float`

    Args:
        period (int): How many Periods to use. Defaults to 14
        source (str): Which input field to calculate the Indicator. Defaults to "close"
    """

    _name: str = field(init=False, default="RSI")
    period: int = 14
    source: Source = "close"

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

        if losses == 0:
            return 100.0 if gains > 0 else None

        return 100.0 - (100.0 / (1.0 + (gains / losses)))
