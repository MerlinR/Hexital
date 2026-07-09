from dataclasses import dataclass, field

from ..core.indicator import Indicator, Source
from .bbands import BBANDS


@dataclass(kw_only=True)
class BandWidth(Indicator[float | None]):
    """Bollinger BandWidth - BBB

    BandWidth expresses the Bollinger Band spread relative to the middle band.

    Sources:
        https://tradingstrategy.ai/docs/api/technical-analysis/volatility/help/pandas_ta.volatility.bbands.html

    Output type: `float`

    Args:
        period (int): How many periods to use. Defaults to 5.
        source (str): Which input field to calculate the indicator from.
            Defaults to `"close"`.
        std (float): Standard deviation multiplier. Defaults to 2.0.
    """

    _name: str = field(init=False, default="BBB")
    period: int = 5
    source: Source = "close"
    std: float = 2.0

    def _generate_name(self) -> str:
        return f"{self._name}_{self.period}_{self.std}{self.source_label()}"

    def _initialise(self):
        self.sub_bbands = self.add_child(
            BBANDS(source=self.source, period=self.period, std=self.std),
        )

    def _calculate_reading(self, index: int) -> float | None:
        bands = self.sub_bbands.reading()
        if bands is None:
            return None

        lower = bands.get("BBL")
        middle = bands.get("BBM")
        upper = bands.get("BBU")

        if lower is None or middle in (None, 0) or upper is None:
            return None

        return 100 * ((upper - lower) / middle)
