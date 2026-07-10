from dataclasses import dataclass, field

from ..core.indicator import Indicator
from .roc import ROC
from .sma import SMA


@dataclass(kw_only=True)
class KST(Indicator[dict[str, float | None]]):
    """Know Sure Thing - KST

    KST combines four smoothed rate-of-change series into a weighted momentum
    oscillator with a signal line.

    Sources:
        https://tradingstrategy.ai/docs/api/technical-analysis/momentum/help/pandas_ta.momentum.kst.html

    Output type: `Dict["KST": float, "signal": float]`
    """

    _name: str = field(init=False, default="KST")
    roc1: int = 10
    roc2: int = 15
    roc3: int = 20
    roc4: int = 30
    sma1: int = 10
    sma2: int = 10
    sma3: int = 10
    sma4: int = 15
    signal_period: int = 9

    def _name_parts(self) -> list[str]:
        return [
            "roc1",
            "roc2",
            "roc3",
            "roc4",
            "sma1",
            "sma2",
            "sma3",
            "sma4",
            "signal_period",
        ]

    def _initialise(self):
        self._state = self.add_state()

        self.sub_roc1 = self.add_child(ROC(name=f"{self.name}_roc1", period=self.roc1))
        self.sub_roc2 = self.add_child(ROC(name=f"{self.name}_roc2", period=self.roc2))
        self.sub_roc3 = self.add_child(ROC(name=f"{self.name}_roc3", period=self.roc3))
        self.sub_roc4 = self.add_child(ROC(name=f"{self.name}_roc4", period=self.roc4))

        self.sub_sma1 = self.sub_roc1.add_child_after(
            SMA(name=f"{self.name}_sma1", source=self.sub_roc1, period=self.sma1)
        )
        self.sub_sma2 = self.sub_roc2.add_child_after(
            SMA(name=f"{self.name}_sma2", source=self.sub_roc2, period=self.sma2)
        )
        self.sub_sma3 = self.sub_roc3.add_child_after(
            SMA(name=f"{self.name}_sma3", source=self.sub_roc3, period=self.sma3)
        )
        self.sub_sma4 = self.sub_roc4.add_child_after(
            SMA(name=f"{self.name}_sma4", source=self.sub_roc4, period=self.sma4)
        )

        self.sub_signal = self.add_child_managed(
            SMA(
                name=f"{self.name}_signal",
                source=self._state.source("kst"),
                period=self.signal_period,
            )
        )

    def _calculate_reading(self, index: int) -> dict[str, float | None]:
        sma1 = self.sub_sma1.reading()
        sma2 = self.sub_sma2.reading()
        sma3 = self.sub_sma3.reading()
        sma4 = self.sub_sma4.reading()

        if sma1 is None or sma2 is None or sma3 is None or sma4 is None:
            return {"KST": None, "signal": None}

        kst = 100 * (sma1 + (2 * sma2) + (3 * sma3) + (4 * sma4))
        self._state.set({"kst": kst})
        self.sub_signal.calculate_index(index)

        return {"KST": kst, "signal": self.sub_signal.reading()}
