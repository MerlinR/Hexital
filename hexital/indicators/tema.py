from dataclasses import dataclass, field

from ..core.indicator import Indicator, Source
from .ema import EMA


@dataclass(kw_only=True)
class TEMA(Indicator[float | None]):
    """Triple Exponential Moving Average - TEMA

    TEMA reduces lag further than DEMA by combining three EMA layers into one
    smoothed output.

    Sources:
        https://tradingstrategy.ai/docs/api/technical-analysis/overlap/help/pandas_ta.overlap.tema.html

    Output type: `float`

    Args:
        period (int): How many periods to use. Defaults to 10.
        source (str): Which input field to calculate the indicator from.
            Defaults to `"close"`.
    """

    _name: str = field(init=False, default="TEMA")
    period: int = 10
    source: Source = "close"

    def _generate_name(self) -> str:
        return f"{self._name}_{self.period}"

    def _initialise(self):
        self.sub_ema = self.add_child(EMA(source=self.source, period=self.period))
        self.sub_ema2 = self.sub_ema.add_child_after(
            EMA(source=self.sub_ema, period=self.period),
        )
        self.sub_ema3 = self.sub_ema2.add_child_after(
            EMA(source=self.sub_ema2, period=self.period),
        )

    def _calculate_reading(self, index: int) -> float | None:
        ema = self.sub_ema.reading()
        ema2 = self.sub_ema2.reading()
        ema3 = self.sub_ema3.reading()

        if ema is None or ema2 is None or ema3 is None:
            return None

        return (3 * ema) - (3 * ema2) + ema3
