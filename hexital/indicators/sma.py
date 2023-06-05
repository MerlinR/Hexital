from dataclasses import dataclass

from hexital.types import Indicator


@dataclass(kw_only=True)
class SMA(Indicator):
    """Simple Moving Average (SMA)

    The Simple Moving Average is the classic moving average that is the equally
    weighted average over n periods.

    Sources:
        https://www.investopedia.com/terms/s/sma.asp

    Args:
        Input value (str): Default Close
        period (int) Default: 10


    """

    indicator_name: str = "SMA"
    input_value: str = "close"
    period: int = 10

    def _generate_name(self) -> str:
        return f"{self.indicator_name}_{self.period}"

    def _calculate_new_value(self, index: int = -1) -> float | dict | None:
        if self.prev_exists(index):
            return self.get_indicator_by_index(index - 1) - (
                self.get_indicator_by_index(index - self.period, self.input_value)
                - self.get_indicator_by_index(index, self.input_value)
            ) / float(self.period)

        if self.get_indicator_period(self.period - 1, index, self.input_value):
            return (
                float(
                    sum(
                        self.get_indicator_by_index(i, self.input_value)
                        for i in range(index - (self.period - 1), index + 1)
                    )
                )
                / self.period
            )

        return None
