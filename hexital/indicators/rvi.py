from dataclasses import dataclass, field

from hexital.core.indicator import Indicator, Managed
from hexital.indicators.ema import EMA
from hexital.indicators.stdev import STDEV


@dataclass(kw_only=True)
class RVI(Indicator):
    """Relative Vigor Index - RVI

    The Relative Vigor Index, or RVI, is a popular member of the “Oscillator” family of technical indicators.
    although the creator of the Relative Vigor Index is unknown, its design is very similar to Stochastics
    except that the closing price is compared with the Open rather than the Low price for the period.

    Sources:
        https://www.thinkmarkets.com/en/learn-to-trade/indicators-and-patterns/indicators/relative-vigor-index-rvi-indicator/

    Output type: `float`

    Args:
        period (int): How many Periods to use. Defaults to 14
        source (str): Which input field to calculate the Indicator. Defaults to "close"
    """

    _name: str = field(init=False, default="RVI")
    period: int = 14
    source: str = "close"
    _scalar: float = field(init=False, default=100.0)

    def _generate_name(self) -> str:
        return f"{self._name}_{self.period}"

    def _initialise(self):
        self.add_sub_indicator(
            STDEV(
                source=self.source,
                period=self.period,
                name=f"{self._name}_stdev",
            ),
        )
        self.add_managed_indicator("data", Managed(name=f"{self._name}_data"))
        self.add_managed_indicator(
            "pos_ema",
            EMA(
                period=self.period,
                source=f"{self._name}_data.pos",
                name=f"{self._name}_pos_ema",
            ),
        )
        self.add_managed_indicator(
            "neg_ema",
            EMA(
                period=self.period,
                source=f"{self._name}_data.neg",
                name=f"{self._name}_neg_ema",
            ),
        )

    def _calculate_reading(self, index: int) -> float | dict | None:
        stdev_reading = self.reading(f"{self._name}_stdev")

        if stdev_reading is not None:
            prev_reading = self.prev_reading(self.source)

            if prev_reading is None:
                return None

            cur_reading = self.reading(self.source)

            pos = 0 if cur_reading <= prev_reading else 1
            neg = 0 if cur_reading >= prev_reading else 1

            pos_stdev = pos * stdev_reading
            neg_stdev = neg * stdev_reading
            self.managed_indicators["data"].set_reading({"pos": pos_stdev, "neg": neg_stdev})
            self.managed_indicators["pos_ema"].calculate_index(index)
            self.managed_indicators["neg_ema"].calculate_index(index)

        positive_smoothed = self.reading(f"{self._name}_pos_ema")
        negative_smoothed = self.reading(f"{self._name}_neg_ema")

        if self.prev_exists() or positive_smoothed is not None:
            return (self._scalar * positive_smoothed) / (positive_smoothed + negative_smoothed)

        return None
