from dataclasses import dataclass

from hexital.types import ATR, Indicator


@dataclass(kw_only=True)
class SMA(Indicator):
    """Supertrend"""

    indicator_name: str = "Supertrend"
    input_value: str = "close"
    period: int = 10

    def _generate_name(self) -> str:
        return f"{self.indicator_name}_{self.period}"

    def _initialise(self):
        self.add_sub_indicator(
            ATR(
                candles=self.candles,
                input_value=self.input_value,
                period=self.period,
                fullname_override=f"{self.indicator_name}_ATR",
            )
        )

    def _calculate_reading(self, index: int = -1) -> float | dict | None:

        return None
