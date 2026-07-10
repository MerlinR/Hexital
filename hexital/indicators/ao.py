from dataclasses import dataclass, field

from ..core.indicator import Indicator
from .sma import SMA


@dataclass(kw_only=True)
class AO(Indicator[float | None]):
    """Awesome Oscillator - AO

    Awesome Oscillator compares a fast and slow simple moving average of the
    median price.

    Sources:
        https://tradingstrategy.ai/docs/api/technical-analysis/momentum/help/pandas_ta.momentum.ao.html

    Output type: `float`

    Args:
        fast (int): Fast SMA length. Defaults to 5.
        slow (int): Slow SMA length. Defaults to 34.
    """

    _name: str = field(init=False, default="AO")
    fast: int = 5
    slow: int = 34

    def _name_parts(self) -> list[str]:
        return ["fast", "slow"]

    def _validate_fields(self):
        if self.slow < self.fast:
            self.fast, self.slow = self.slow, self.fast

    def _initialise(self):
        self._state = self.add_state()
        self.sub_fast = self.add_child_managed(
            SMA(
                name=f"{self.name}_fast",
                source=self._state.source("median"),
                period=self.fast,
            )
        )
        self.sub_slow = self.add_child_managed(
            SMA(
                name=f"{self.name}_slow",
                source=self._state.source("median"),
                period=self.slow,
            )
        )

    def _calculate_reading(self, index: int) -> float | None:
        self._state.set({"median": 0.5 * (self.high + self.low)})
        self.sub_fast.calculate_index(index)
        self.sub_slow.calculate_index(index)

        fast = self.sub_fast.reading()
        slow = self.sub_slow.reading()
        if fast is None or slow is None:
            return None

        return fast - slow
