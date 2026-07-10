from dataclasses import dataclass, field

from ..core.indicator import Indicator, Source
from .ema import EMA


@dataclass(kw_only=True)
class TSI(Indicator[float | None]):
    """True Strength Index - TSI
    TSI attempts to show both trend direction and overbought/oversold conditions,
    using moving averages of the underlying momentum of a financial instrument.

    Sources:
        https://school.stockcharts.com/doku.php?id=technical_indicators:true_strength_index

    Output type: `float`

    Args:
        period (int): How many Periods to use. Defaults to 25
        smooth_period (int): How much to smooth with EMA defaults: (period / 2) + (period % 2 > 0). Defaults to halve of period
        source (str): Which input field to calculate the Indicator. Defaults to "close"

    """

    _name: str = field(init=False, default="TSI")
    period: int = 25
    smooth_period: int = 0
    source: Source = "close"

    def _name_parts(self) -> list[str]:
        return ["period", "smooth_period", "source"]

    def _validate_fields(self):
        if self.smooth_period == 0:
            self.smooth_period = int(int(self.period / 2) + (self.period % 2 > 0))

    def _initialise(self):
        self._state = self.add_state()

        self.sub_first = self._state.managed.add_child_after(
            EMA(
                source=self._state.source("price"),
                period=self.period,
                name=f"{self.name}_first",
            ),
        )

        self.sub_second = self.sub_first.add_child_after(
            EMA(source=self.sub_first, period=self.smooth_period),
        )

        self.abs_first = self._state.managed.add_child_after(
            EMA(source=self._state.source("abs_price"), period=self.period),
        )
        self.abs_second = self.abs_first.add_child_after(
            EMA(source=self.abs_first, period=self.smooth_period),
        )

    def _calculate_reading(self, index: int) -> float | None:
        prev_reading = self.prev_src()
        if prev_reading is None:
            return None

        source = self.src()

        if source is None:
            return None

        self._state.update(
            price=source - prev_reading,
            abs_price=abs(source - prev_reading),
        )

        abs_second = self.abs_second.reading()
        if abs_second is not None:
            return 100 * (self.sub_second.reading() / abs_second)

        return None
