from dataclasses import dataclass, field

from ..core.indicator import Indicator, Source
from ..exceptions import InvalidIndicator
from .ema import EMA
from .sma import SMA
from .tr import TR


@dataclass(kw_only=True)
class KC(Indicator[dict[str, float | None]]):
    """Keltner Channel - KC

    Keltner channel is a technical analysis indicator showing a central moving
    average line plus channel lines at a distance above and below.
    A popular volatility indicator similar to Bollinger Bands and Donchian Channels.

    Sources:
        https://www.investopedia.com/terms/k/keltnerchannel.asp

    Output type: `Dict["lower": float, "band": float, "upper": float]`

    Args:
        period (int): How many Periods to use. Defaults to 20
        source (str): Which input field to calculate the Indicator. Defaults to "close"
        multiplier (float): A positive float to multiply the bands. Defaults to 2.0
        mamode (str): Center line average type. One of `"ema"` or `"sma"`.
            Defaults to `"ema"`
        tr (bool): Use true range for the channel width. Defaults to `True`
    """

    _name: str = field(init=False, default="KC")
    period: int = 20
    source: Source = "close"
    multiplier: float = 2.0
    mamode: str = "ema"
    tr: bool = True

    def _name_parts(self) -> list[str]:
        return ["period", "mamode", "multiplier", "source"]

    def _validate_fields(self):
        self.mamode = self.mamode.lower()
        if self.mamode not in {"ema", "sma"}:
            raise InvalidIndicator(
                f"Invalid mamode {self.mamode!r}; expected 'ema' or 'sma'"
            )

    def _initialise(self):
        self._range_state = self.add_state(name=f"{self.name}_range")

        average_indicator: EMA | SMA
        if self.mamode == "sma":
            average_indicator = SMA(
                name=f"{self.name}_basis",
                source=self.source,
                period=self.period,
            )
        else:
            average_indicator = EMA(
                name=f"{self.name}_basis",
                source=self.source,
                period=self.period,
            )
        self.sub_ma = self.add_child(average_indicator)

        if self.tr:
            self.sub_tr = self.add_child(TR(name=f"{self.name}_tr"))

        range_average_indicator: EMA | SMA
        if self.mamode == "sma":
            range_average_indicator = SMA(
                name=f"{self.name}_range_ma",
                source=self._range_state.managed,
                period=self.period,
            )
        else:
            range_average_indicator = EMA(
                name=f"{self.name}_range_ma",
                source=self._range_state.managed,
                period=self.period,
            )
        self.sub_range_ma = self.add_child_managed(range_average_indicator)

    def _calculate_reading(self, index: int) -> dict[str, float | None]:
        ma_ = self.sub_ma.reading()
        if self.tr:
            range_ = self.sub_tr.reading()
        else:
            range_ = self.high - self.low

        self._range_state.set(range_)
        self.sub_range_ma.calculate_index(index)

        range_ma = self.sub_range_ma.reading()

        if ma_ is None or range_ma is None:
            return {"lower": None, "band": ma_, "upper": None}

        lower = ma_ - (self.multiplier * range_ma)
        upper = ma_ + (self.multiplier * range_ma)

        return {"lower": lower, "band": ma_, "upper": upper}
