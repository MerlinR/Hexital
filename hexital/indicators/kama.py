from dataclasses import dataclass, field

from ..core.indicator import Indicator, Source
from ..utils.common import non_zero_range


@dataclass(kw_only=True)
class KAMA(Indicator[float | None]):
    """Kaufman's Adaptive Moving Average - KAMA

    KAMA adapts its smoothing based on market efficiency. It responds faster in
    directional moves and slows down in noisy ranges.

    Sources:
        https://tradingstrategy.ai/docs/api/technical-analysis/overlap/help/pandas_ta.overlap.kama.html

    Output type: `float`

    Args:
        period (int): Efficiency ratio lookback. Defaults to 10.
        fast (int): Fast EMA length. Defaults to 2.
        slow (int): Slow EMA length. Defaults to 30.
        source (str): Which input field to calculate the indicator from.
            Defaults to `"close"`.
    """

    _name: str = field(init=False, default="KAMA")
    period: int = 10
    fast: int = 2
    slow: int = 30
    source: Source = "close"
    _fast_alpha: float = field(init=False, default=0.0)
    _slow_alpha: float = field(init=False, default=0.0)

    def _generate_name(self) -> str:
        return f"{self._name}_{self.period}_{self.fast}_{self.slow}{self.source_label()}"

    def _validate_fields(self):
        self._fast_alpha = 2.0 / (self.fast + 1.0)
        self._slow_alpha = 2.0 / (self.slow + 1.0)

    def _calculate_reading(self, index: int) -> float | None:
        if (prev_kama := self.prev_reading()) is not None:
            return self._calculate_kama(index, prev_kama)

        if self.reading_period(self.period, self.source):
            return 0.0

        return None

    def _calculate_kama(self, index: int, prev_kama: float) -> float | None:
        reading = self.src()
        period_back = self.at_src(index - self.period)
        if reading is None or period_back is None:
            return None

        change = non_zero_range(reading, period_back)
        volatility = 0.0

        for pointer in range(index - self.period + 1, index + 1):
            current = self.at_src(pointer)
            previous = self.at_src(pointer - 1)
            if current is None or previous is None:
                return None
            volatility += non_zero_range(current, previous)

        efficiency_ratio = change / volatility
        smoothing = (
            efficiency_ratio * (self._fast_alpha - self._slow_alpha)
        ) + self._slow_alpha
        smoothing_constant = smoothing * smoothing

        return (smoothing_constant * reading) + ((1.0 - smoothing_constant) * prev_kama)
