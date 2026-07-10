from dataclasses import dataclass, field

from ..core.indicator import Indicator, Source
from .ema import EMA
from .sma import SMA


@dataclass(kw_only=True)
class TRIX(Indicator[dict[str, float | None]]):
    """Triple Exponential Average Oscillator - TRIX

    TRIX measures the percent rate of change of a triple-smoothed EMA and
    pairs it with a simple moving average signal line.

    Sources:
        https://tradingstrategy.ai/docs/api/technical-analysis/momentum/help/pandas_ta.momentum.trix.html

    Output type: `Dict["TRIX": float, "signal": float]`

    Args:
        period (int): EMA lookback. Defaults to 30.
        signal_period (int): Signal SMA lookback. Defaults to 9.
        scalar (float): Multiplier applied to the percent change. Defaults to 100.0.
        source (str): Which input field to calculate the indicator from.
            Defaults to `"close"`.
    """

    _name: str = field(init=False, default="TRIX")
    period: int = 30
    signal_period: int = 9
    scalar: float = 100.0
    source: Source = "close"

    def _name_parts(self) -> list[str]:
        return ["period", "signal_period", "source"]

    def _initialise(self):
        self._trix = self.add_state(name=f"{self.name}_trix")

        self.sub_ema = self.add_child(EMA(source=self.source, period=self.period))
        self.sub_ema2 = self.sub_ema.add_child_after(
            EMA(source=self.sub_ema, period=self.period),
        )
        self.sub_ema3 = self.sub_ema2.add_child_after(
            EMA(source=self.sub_ema2, period=self.period),
        )
        self.sub_signal = self.add_child_managed(
            SMA(source=self._trix.managed, period=self.signal_period),
        )

    def _calculate_reading(self, index: int) -> dict[str, float | None]:
        ema3 = self.sub_ema3.reading()
        prev_ema3 = self.sub_ema3.prev_reading()

        if ema3 is None or prev_ema3 in (None, 0):
            return {"TRIX": None, "signal": None}

        trix = self.scalar * ((ema3 - prev_ema3) / prev_ema3)

        self._trix.set(trix)
        self.sub_signal.calculate_index(index)

        return {"TRIX": trix, "signal": self.sub_signal.reading()}
