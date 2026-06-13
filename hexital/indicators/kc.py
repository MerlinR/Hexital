from dataclasses import dataclass, field

from ..exceptions import InvalidIndicator
from ..core.indicator import Indicator, Source
from .atr import ATR
from .ema import EMA
from .sma import SMA


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
    """

    _name: str = field(init=False, default="KC")
    period: int = 20
    source: Source = "close"
    multiplier: float = 2.0
    mamode: str = "ema"

    def _generate_name(self) -> str:
        name = f"{self._name}_{self.period}_{self.multiplier}"
        if self.mamode != "ema":
            name += f"_{self.mamode}"
        return name

    def _validate_fields(self):
        self.mamode = self.mamode.lower()
        if self.mamode not in {"ema", "sma"}:
            raise InvalidIndicator(
                f"Invalid mamode {self.mamode!r}; expected 'ema' or 'sma'"
            )

    def _initialise(self):
        self.sub_atr = self.add_child(ATR(period=self.period))
        average_indicator: EMA | SMA
        if self.mamode == "sma":
            average_indicator = SMA(source=self.source, period=self.period)
        else:
            average_indicator = EMA(source=self.source, period=self.period)
        self.sub_ma = self.add_child(average_indicator)

    def _calculate_reading(self, index: int) -> dict[str, float | None]:
        atr_ = self.sub_atr.reading()
        ma_ = self.sub_ma.reading()

        if atr_ is None:
            return {"lower": None, "band": ma_, "upper": None}

        lower = ma_ - (self.multiplier * atr_)
        upper = ma_ + (self.multiplier * atr_)

        return {"lower": lower, "band": ma_, "upper": upper}
