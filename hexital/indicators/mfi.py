from dataclasses import dataclass, field

from hexital.core.indicator import Indicator, Managed
from hexital.indicators.hlca import HLCA


@dataclass(kw_only=True)
class MFI(Indicator):
    """Money Flow Index - MFI

    The money flow index (MFI) is an oscillator that ranges from 0 to 100.
    It is used to show the money flow over several days.

    Sources:
        https://www.tradingview.com/wiki/Money_Flow_(MFI)

    Output type: `float`

    Args:
        period (int): How many Periods to use. Defaults to 14
        source (str): Which input field to calculate the Indicator. Defaults to "close"
    """

    _name: str = field(init=False, default="MFI")
    period: int = 14
    source: str = "close"

    def _generate_name(self) -> str:
        return f"{self._name}_{self.period}"

    def _initialise(self):
        self.add_sub_indicator(HLCA())
        self.add_managed_indicator("data", Managed(name=f"{self.name}_data"))

    def _calculate_reading(self, index: int) -> float | dict | None:
        hlca = self.reading("HLCA")
        prev_hlca = self.prev_reading("HLCA")

        money_flow = hlca * self.candles[index].volume

        if prev_hlca and hlca > prev_hlca:
            self.managed_indicators["data"].set_reading({"positive": money_flow, "negative": 0})
        elif prev_hlca and hlca < prev_hlca:
            self.managed_indicators["data"].set_reading({"positive": 0, "negative": money_flow})
        elif prev_hlca and hlca == prev_hlca:
            self.managed_indicators["data"].set_reading({"positive": 0, "negative": 0})

        if self.prev_exists() or self.reading_period(self.period + 1, "HLCA", index):
            pos_money = self.candles_sum(self.period, f"{self.name}_data.positive")
            neg_money = self.candles_sum(self.period, f"{self.name}_data.negative")

            if pos_money and neg_money:
                return 100 * (pos_money / (pos_money + neg_money))

            return 0

        return None
