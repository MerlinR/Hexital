from dataclasses import dataclass, field

from ..core.indicator import Indicator, Source
from .ema import EMA
from .sma import SMA


@dataclass(kw_only=True)
class PPO(Indicator[dict[str, float | None]]):
    """Percentage Price Oscillator - PPO

    PPO measures the percentage difference between a fast and slow moving
    average, and returns the PPO line along with its signal line and histogram.

    Output type: `Dict["PPO": float, "Signal": float, "Histogram": float]`

    Args:
        source (str): Which input field to calculate the Indicator. Defaults to "close"
        fast_period (int): How many Periods to use for fast average. Defaults to 12
        slow_period (int): How many Periods to use for slow average. Defaults to 26
        signal_period (int): How many Periods to use for signal average. Defaults to 9
    """

    _name: str = field(init=False, default="PPO")
    source: Source = "close"
    fast_period: int = 12
    slow_period: int = 26
    signal_period: int = 9

    def _generate_name(self) -> str:
        return f"{self._name}_{self.fast_period}_{self.slow_period}_{self.signal_period}{self.source_label()}"

    def _validate_fields(self):
        if self.slow_period < self.fast_period:
            self.fast_period, self.slow_period = self.slow_period, self.fast_period

    def _initialise(self):
        self._ppo = self.add_state(name=f"{self.name}_ppo")

        self.sub_fast = self.add_child(SMA(source=self.source, period=self.fast_period))
        self.sub_slow = self.add_child(SMA(source=self.source, period=self.slow_period))
        self.sub_signal = self.add_child_managed(
            EMA(source=self._ppo.managed, period=self.signal_period),
        )

    def _calculate_reading(self, index: int) -> dict[str, float | None]:
        avg_slow = self.sub_slow.reading()

        if not avg_slow:
            return {"PPO": None, "Signal": None, "Histogram": None}

        ppo = ((self.sub_fast.reading() - avg_slow) / avg_slow) * 100.0

        self._ppo.set(ppo)
        self.sub_signal.calculate_index(index)

        signal = self.sub_signal.reading()
        if signal is None:
            return {"PPO": ppo, "Signal": None, "Histogram": None}

        return {
            "PPO": ppo,
            "Signal": signal,
            "Histogram": ppo - signal,
        }
