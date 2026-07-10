from dataclasses import dataclass, field

from ..core.indicator import Indicator
from .roc import ROC
from .wma import WMA


@dataclass(kw_only=True)
class COPC(Indicator[float | None]):
    """Coppock Curve - COPC

    Coppock Curve is a weighted moving average of the sum of two rate-of-change
    series.

    Sources:
        https://tradingstrategy.ai/docs/api/technical-analysis/momentum/help/pandas_ta.momentum.coppock.html

    Output type: `float`

    Args:
        period (int): WMA smoothing length. Defaults to 10.
        fast (int): Fast ROC length. Defaults to 11.
        slow (int): Slow ROC length. Defaults to 14.
    """

    _name: str = field(init=False, default="COPC")
    period: int = 10
    fast: int = 11
    slow: int = 14

    def _name_parts(self) -> list[str]:
        return ["fast", "slow", "period"]

    def _validate_fields(self):
        if self.slow < self.fast:
            self.fast, self.slow = self.slow, self.fast

    def _initialise(self):
        self._state = self.add_state()
        self.sub_fast = self.add_child(ROC(name=f"{self.name}_fast", period=self.fast))
        self.sub_slow = self.add_child(ROC(name=f"{self.name}_slow", period=self.slow))
        self.sub_wma = self.add_child_managed(
            WMA(
                name=f"{self.name}_wma",
                source=self._state.source("roc_sum"),
                period=self.period,
            )
        )

    def _calculate_reading(self, index: int) -> float | None:
        fast = self.sub_fast.reading()
        slow = self.sub_slow.reading()
        if fast is None or slow is None:
            return None

        self._state.set({"roc_sum": fast + slow})
        self.sub_wma.calculate_index(index)
        return self.sub_wma.reading()
