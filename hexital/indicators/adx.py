from dataclasses import dataclass, field
from typing import Optional

from hexital.core.indicator import Indicator, Managed
from hexital.indicators.atr import ATR
from hexital.indicators.rma import RMA


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

    _name: str = field(init=False, default="ADX")

    period: int = 14
    period_signal: Optional[int] = None

    def _generate_name(self) -> str:
        return f"{self._name}_{self.period}_{self.period_signal}"

    def _validate_fields(self):
        if self.period_signal is None:
            self.period_signal = self.period

    def _initialise(self):
        self.add_sub_indicator(
            ATR(
                period=self.period,
                fullname_override=f"{self.name}_atr",
            )
        )
        data_indicator = Managed(fullname_override=f"{self.name}_data")
        self.add_managed_indicator("ADX_data", data_indicator)

        data_indicator.add_sub_indicator(
            RMA(
                fullname_override=f"{self.name}_pos",
                period=self.period,
                input_value=f"{self.name}_data.pos",
            ),
            False,
        )
        data_indicator.add_sub_indicator(
            RMA(
                fullname_override=f"{self.name}_neg",
                period=self.period,
                input_value=f"{self.name}_data.neg",
            ),
            False,
        )
        self.add_managed_indicator(
            "dx",
            RMA(
                fullname_override=f"{self.name}_dx",
                period=self.period_signal,
                input_value=f"{self.name}_data.dx",
            ),
        )

    def _calculate_reading(self, index: int) -> float | dict | None:
        adx_final = None
        adx_positive = None
        adx_negative = None

        if self.reading("high"):
            up = self.reading("high") - self.reading("high", index - 1)
            down = self.reading("low", index - 1) - self.reading("low")

            positive = up if up > down and up > 0 else 0
            negative = down if down > up and down > 0 else 0
            self.managed_indicators["ADX_data"].set_reading({"pos": positive, "neg": negative})

            if self.reading(f"{self.name}_atr") and self.reading(f"{self.name}_pos"):
                mod = 100 / self.reading(f"{self.name}_atr")

                adx_positive = mod * self.reading(f"{self.name}_pos")
                adx_negative = mod * self.reading(f"{self.name}_neg")

                dx = 100 * abs(adx_positive - adx_negative) / (adx_positive + adx_negative)

                self.managed_indicators["ADX_data"].set_reading(
                    {"pos": positive, "neg": negative, "dx": dx}
                )
                self.managed_indicators["dx"].calculate_index(index)

                if self.reading(f"{self.name}_dx"):
                    adx_final = self.reading(f"{self.name}_dx")

        return {"ADX": adx_final, "DM_Plus": adx_positive, "DM_Neg": adx_negative}
