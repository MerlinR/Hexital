import math
from dataclasses import dataclass, field

from hexital.core.indicator import Indicator, Managed, NestedSource, Source


@dataclass(kw_only=True)
class JMA(Indicator[float | None]):
    """Jurik Moving Average Average - JMA

    The JMA is an adaptive moving average that aims to reduce lag and improve responsiveness
    to price changes compared to traditional moving averages.
    By incorporating volatility and phase shift components, the JMA seeks to provide traders
    with a more accurate and timely representation of market trends.

    Sources:
        https://c.mql5.com/forextsd/forum/164/jurik_1.pdf

    Args:
        period (int): How many Periods to use. Defaults to 7
        source (str): Which input field to calculate the Indicator. Defaults to "close"
        phase (float): How heavy/light the average is [-100, 100]. Defaults to 0.0

    """

    _name: str = field(init=False, default="JMA")
    period: int = 7
    source: Source = "close"
    phase: float = 0.0

    _phase_ratio: float = field(init=False, default=0)
    _beta: float = field(init=False, default=0)
    _length_1: float = field(init=False, default=0)
    _length_2: float = field(init=False, default=0)
    _power_1: float = field(init=False, default=0)
    _bet: float = field(init=False, default=0)

    def _generate_name(self) -> str:
        return f"{self._name}_{self.period}_{self.phase}"

    def _initialise(self):
        self.data = self.add_managed_indicator(Managed())

    def _validate_fields(self):
        if self.phase > 100:
            self.phase = 100.0
        elif self.phase < -100:
            self.phase = -100.0
        self._phase_ratio = 1.5 + self.phase * 0.01

        self._beta = 0.45 * (self.period - 1) / (0.45 * (self.period - 1) + 2)

        length_ = 0.5 * (self.period - 1)
        self._length_1 = max((math.log(math.sqrt(length_)) / math.log(2.0)) + 2.0, 0)
        self._length_2 = self._length_1 * math.sqrt(length_)

        self._power_1 = max(self._length_1 - 2.0, 0.5)
        self._bet = self._length_2 / (self._length_2 + 1)

    def _calculate_reading(self, index: int) -> float | None:
        price = self.reading(self.source)
        uband = self.prev_reading(NestedSource(self.data, "uband"), price)
        lband = self.prev_reading(NestedSource(self.data, "lband"), price)
        vsums = self.prev_reading(NestedSource(self.data, "vsums"), 0)
        ma_one = self.prev_reading(NestedSource(self.data, "ma_one"), price)
        ma_two = self.prev_reading(NestedSource(self.data, "ma_two"), 0)
        det_one = self.prev_reading(NestedSource(self.data, "det_one"), 0)
        det_two = self.prev_reading(NestedSource(self.data, "det_two"), 0)

        # Price Volatility
        del1 = price - uband
        del2 = price - lband
        volty = max(abs(del1), abs(del2)) if abs(del1) != abs(del2) else 0
        self.data.set_reading({"volty": volty})

        # Relative Price Volatility
        vsums = self.candles_average(10, NestedSource(self.data, "volty"))
        self.data.set_reading({"vsums": vsums, "volty": volty})

        avg_volty = self.candles_average(65, NestedSource(self.data, "vsums"))
        d_volty = 0 if avg_volty == 0 else volty / avg_volty
        r_volt = max(1.0, min(pow(self._length_1, 1 / self._power_1), d_volty))

        # Jurik Volatility Bands
        power_2 = pow(r_volt, self._power_1)
        kv = pow(self._bet, math.sqrt(power_2))
        uband = price if (del1 > 0) else price - (kv * del1)
        lband = price if (del2 < 0) else price - (kv * del2)

        power = pow(r_volt, self._power_1)
        alpha = pow(self._beta, power)

        # Stage One
        ma_one = ((1 - alpha) * price) + (alpha * ma_one)

        # Stage Two
        det_one = ((price - ma_one) * (1 - self._beta)) + (self._beta * det_one)
        ma_two = ma_one + self._phase_ratio * det_one

        # Stage Three
        det_two = ((ma_two - self.prev_reading(default=price)) * (1 - alpha) * (1 - alpha)) + (
            alpha * alpha * det_two
        )
        jma = self.prev_reading(default=price) + det_two

        self.data.set_reading(
            {
                "uband": uband,
                "lband": lband,
                "vsums": vsums,
                "volty": volty,
                "ma_one": ma_one,
                "ma_two": ma_two,
                "det_one": det_one,
                "det_two": det_two,
            }
        )

        return jma
