from dataclasses import dataclass, field

from hexital.core.indicator import Indicator, Managed, NestedSource, Source
from hexital.indicators.ema import EMA
from hexital.indicators.stdev import STDEV


@dataclass(kw_only=True)
class RVI(Indicator[float | None]):
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
    source: Source = "close"
    _scalar: float = field(init=False, default=100.0)

    def _generate_name(self) -> str:
        return f"{self._name}_{self.period}"

    def _initialise(self):
        self.data = self.add_managed_indicator(Managed())

        self.sub_stdev = self.add_sub_indicator(STDEV(source=self.source, period=self.period))
        self.sub_pos = self.add_managed_indicator(
            EMA(
                period=self.period,
                source=NestedSource(self.data, "pos"),
                name=f"{self._name}_pos_ema",
            ),
        )
        self.sub_neg = self.add_managed_indicator(
            EMA(
                period=self.period,
                source=NestedSource(self.data, "neg"),
                name=f"{self._name}_neg_ema",
            ),
        )

    def _calculate_reading(self, index: int) -> float | None:
        stdev_reading = self.sub_stdev.reading()

        if stdev_reading is not None:
            prev_reading = self.prev_reading(self.source)

            if prev_reading is None:
                return None

            cur_reading = self.reading(self.source)

            pos = 0 if cur_reading <= prev_reading else 1
            neg = 0 if cur_reading >= prev_reading else 1

            pos_stdev = pos * stdev_reading
            neg_stdev = neg * stdev_reading

            self.data.set_reading({"pos": pos_stdev, "neg": neg_stdev})
            self.sub_pos.calculate_index(index)
            self.sub_neg.calculate_index(index)

        positive_smoothed = self.sub_pos.reading()
        negative_smoothed = self.sub_neg.reading()

        if self.prev_exists() or positive_smoothed is not None:
            return (self._scalar * positive_smoothed) / (positive_smoothed + negative_smoothed)

        return None
