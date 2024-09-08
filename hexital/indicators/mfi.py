from dataclasses import dataclass, field

from hexital.core.indicator import Indicator, Managed
from hexital.indicators.hlca import HighLowCloseAverage


@dataclass(kw_only=True)
class MFI(Indicator):
    """Money Flow Index (MFI)

    Sources:
        https://www.tradingview.com/wiki/Money_Flow_(MFI)

    Args:
        Input value (str): Default Close
        period (int) Default: 14
    """

    _name: str = field(init=False, default="MFI")
    period: int = 14
    input_value: str = "close"

    def _generate_name(self) -> str:
        return f"{self._name}_{self.period}"

    def _initialise(self):
        self.add_sub_indicator(HighLowCloseAverage())
        self.add_managed_indicator("MFI_Data", Managed(fullname_override=f"{self.name}_data"))

    def _calculate_reading(self, index: int) -> float | dict | None:
        hlca = self.reading("HLCA")
        prev_hlca = self.prev_reading("HLCA")

        money_flow = hlca * self.candles[index].volume

        if prev_hlca and hlca > prev_hlca:
            self.managed_indicators["MFI_Data"].set_reading(
                {"positive": money_flow, "negative": 0}
            )
        elif prev_hlca and hlca < prev_hlca:
            self.managed_indicators["MFI_Data"].set_reading(
                {"positive": 0, "negative": money_flow}
            )
        elif prev_hlca and hlca == prev_hlca:
            self.managed_indicators["MFI_Data"].set_reading({"positive": 0, "negative": 0})

        if not self.prev_exists() and not self.reading_period(self.period + 1, "HLCA", index):
            return None

        pos_money = self.candles_sum(self.period, f"{self.name}_data.positive")
        neg_money = self.candles_sum(self.period, f"{self.name}_data.negative")

        if pos_money and neg_money:
            return 100 * (pos_money / (pos_money + neg_money))

        return 0
