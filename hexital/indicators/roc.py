from dataclasses import dataclass, field

from hexital.core.indicator import Indicator


@dataclass(kw_only=True)
class ROC(Indicator):
    """Rate Of Change - ROC

    The Price Rate of Change (ROC) indicator in trading refers to the percentage change
    between the current price and the price of a set number of periods ago.
    It is used to identify the momentum of price movement and help traders make informed
    decisions regarding buying or selling assets. This indicator is calculated by dividing
    the difference between the current price and the price of a set number of periods ago
    by the previous price and multiplying by 100.

    Sources:
        https://en.wikipedia.org/wiki/Momentum_(technical_analysis)

    Output type: `float`

    Args:
        period (int): How many Periods to use. Defaults to 10
        source (str): Which input field to calculate the Indicator. Defaults to "close"
    """

    _name: str = field(init=False, default="ROC")
    period: int = 10
    source: str = "close"

    def _generate_name(self) -> str:
        return f"{self._name}"

    def _calculate_reading(self, index: int) -> float | dict | None:
        if self.prev_exists() or self.reading_period(self.period + 1, self.source):
            period_n_back = self.reading(self.source, index - self.period)

            if period_n_back == 0:
                return -100

            return ((self.reading(self.source) - period_n_back) / period_n_back) * 100
        return None
