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
        self._add_sub_indicator(
            ATR(
                period=self.period,
                fullname_override=f"{self._name}_atr",
            )
        )
        self._add_managed_indicator(
            "positive",
            RMA(
                fullname_override=f"{self._name}_pos",
                period=self.period,
                input_value=f"{self._name}_ppos",
            ),
        )
        self._add_managed_indicator(
            "plain_positive",
            Managed(
                fullname_override=f"{self._name}_ppos",
            ),
        )
        self._add_managed_indicator(
            "negative",
            RMA(
                fullname_override=f"{self._name}_neg",
                period=self.period,
                input_value=f"{self._name}_pneg",
            ),
        )
        self._add_managed_indicator(
            "plain_negative",
            Managed(
                fullname_override=f"{self._name}_pneg",
            ),
        )

        self._add_managed_indicator(
            "dx",
            RMA(
                fullname_override=f"{self._name}_dx",
                period=self.period_signal,
                input_value=f"{self._name}_pdx",
            ),
        )
        self._add_managed_indicator(
            "plain_dx",
            Managed(
                fullname_override=f"{self._name}_pdx",
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

            self._managed_indicators["plain_positive"].set_reading(positive)
            self._managed_indicators["plain_negative"].set_reading(negative)
            self._managed_indicators["positive"].calculate_index(index)
            self._managed_indicators["negative"].calculate_index(index)

            if self.reading(f"{self._name}_atr") and self.reading(f"{self._name}_pos"):
                mod = 100 / self.reading(f"{self._name}_atr")

                adx_positive = mod * self.reading(f"{self._name}_pos")
                adx_negative = mod * self.reading(f"{self._name}_neg")

                dx = 100 * abs(adx_positive - adx_negative) / (adx_positive + adx_negative)

                self._managed_indicators["plain_dx"].set_reading(dx)
                self._managed_indicators["dx"].calculate_index(index)

                if self.reading(f"{self._name}_dx"):
                    adx_final = self.reading(f"{self._name}_dx")

        return {"ADX": adx_final, "DM_Plus": adx_positive, "DM_Neg": adx_negative}
