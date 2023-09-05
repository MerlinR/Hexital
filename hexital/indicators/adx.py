from dataclasses import dataclass
from typing import Optional

from hexital import indicators
from hexital.types import Indicator


@dataclass(kw_only=True)
class ADX(Indicator):
    """Average Directional Index (ADX)

    he trend can be either up or down, and this is shown by two accompanying indicators,
    the negative directional indicator (-DI) and the positive directional indicator (+DI).
    Therefore, the ADX commonly includes three separate lines. These are used to help
    assess whether a trade should be taken long or short,
    or if a trade should be taken at all.

    Sources:
        https://www.investopedia.com/terms/a/adx.asp


    """

    indicator_name: str = "ADX"

    period: int = 14
    period_signal: Optional[int] = None

    def _generate_name(self) -> str:
        return f"{self.indicator_name}_{self.period}_{self.period_signal}"

    def _validate_fields(self):
        if self.period_signal is None:
            self.period_signal = self.period

    def _initialise(self):
        self.add_sub_indicator(
            indicators.ATR(
                candles=self.candles,
                period=self.period,
                fullname_override=f"{self.indicator_name}_atr",
            )
        )
        self.add_managed_indicator(
            "positive",
            indicators.RMA(
                candles=self.candles,
                fullname_override=f"{self.indicator_name}_pos",
                period=self.period,
                input_value=f"{self.indicator_name}_ppos",
            ),
        )
        self.add_managed_indicator(
            "plain_positive",
            indicators.Managed(
                candles=self.candles,
                fullname_override=f"{self.indicator_name}_ppos",
            ),
        )
        self.add_managed_indicator(
            "negative",
            indicators.RMA(
                candles=self.candles,
                fullname_override=f"{self.indicator_name}_neg",
                period=self.period,
                input_value=f"{self.indicator_name}_pneg",
            ),
        )
        self.add_managed_indicator(
            "plain_negative",
            indicators.Managed(
                candles=self.candles,
                fullname_override=f"{self.indicator_name}_pneg",
            ),
        )

        self.add_managed_indicator(
            "dx",
            indicators.RMA(
                candles=self.candles,
                fullname_override=f"{self.indicator_name}_dx",
                period=self.period_signal,
                input_value=f"{self.indicator_name}_pdx",
            ),
        )
        self.add_managed_indicator(
            "plain_dx",
            indicators.Managed(
                candles=self.candles,
                fullname_override=f"{self.indicator_name}_pdx",
            ),
        )

    def _calculate_reading(self, index: int = -1) -> float | dict | None:
        adx_final = None
        adx_positive = None
        adx_negative = None

        if self.reading("high"):

            up = self.reading("high") - self.reading("high", index - 1)
            down = self.reading("low", index - 1) - self.reading("low")

            positive = up if up > down and up > 0 else 0
            negative = down if down > up and down > 0 else 0

            self.managed_indictor("plain_positive").set_reading(positive)
            self.managed_indictor("plain_negative").set_reading(negative)
            self.managed_indictor("positive").calculate_index(index)
            self.managed_indictor("negative").calculate_index(index)

            if self.reading(f"{self.indicator_name}_atr") and self.reading(
                f"{self.indicator_name}_pos"
            ):

                mod = 100 / self.reading(f"{self.indicator_name}_atr")

                adx_positive = mod * self.reading(f"{self.indicator_name}_pos")
                adx_negative = mod * self.reading(f"{self.indicator_name}_neg")

                dx = (
                    100 * abs(adx_positive - adx_negative) / (adx_positive + adx_negative)
                )

                self.managed_indictor("plain_dx").set_reading(dx)
                self.managed_indictor("dx").calculate_index(index)

                if self.reading(f"{self.indicator_name}_dx"):
                    adx_final = self.reading(f"{self.indicator_name}_dx")

        return {"ADX": adx_final, "DM_Plus": adx_positive, "DM_Neg": adx_negative}