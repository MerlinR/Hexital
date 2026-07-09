from dataclasses import dataclass, field

from ..core.indicator import Indicator
from ..exceptions import InvalidIndicator
from .bbands import BBANDS
from .ema import EMA
from .kc import KC
from .sma import SMA


@dataclass(kw_only=True)
class Squeeze(Indicator[dict[str, float | int | None]]):
    """Squeeze

    The TTM Squeeze is a volatility and momentum indicator.
    This implementation matches the default `pandas_ta.squeeze` output used by
    the source-of-truth fixture: Bollinger Bands versus SMA-based Keltner
    Channels plus `mom(12)` smoothed by `sma(6)`.

    Output type: `Dict["SQZ": float, "ON": int, "OFF": int]`

    Args:
        bb_length (int): Bollinger Bands period. Defaults to 20
        bb_std (float): Bollinger Bands standard deviation multiplier. Defaults to 2.0
        kc_length (int): Keltner Channel period. Defaults to 20
        kc_scalar (float): Keltner Channel scalar. Defaults to 1.5
        mom_length (int): Momentum period. Defaults to 12
        mom_smooth (int): Momentum smoothing period. Defaults to 6
        mamode (str): Momentum smoothing average type. One of `"sma"` or `"ema"`
        period (int | None): Backwards-compatible alias for `bb_length` and `kc_length`
    """

    _name: str = field(init=False, default="SQ")
    bb_length: int = 20
    bb_std: float = 2.0
    kc_length: int = 20
    kc_scalar: float = 1.5
    mom_length: int = 12
    mom_smooth: int = 6
    mamode: str = "sma"
    period: int | None = None

    def _generate_name(self) -> str:
        return f"{self._name}_{self.bb_length}_{self.kc_length}_{self.mamode}_{self.mom_length}_{self.mom_smooth}"

    def _validate_fields(self):
        if self.period is not None:
            self.bb_length = self.period
            self.kc_length = self.period

        self.mamode = self.mamode.lower()
        if self.mamode not in {"sma", "ema"}:
            raise InvalidIndicator(
                f"Invalid mamode {self.mamode!r}; expected 'sma' or 'ema'"
            )

    def _initialise(self):
        self._momentum = self.add_state(name=f"{self.name}_momentum")

        self.sub_bbands = self.add_child(
            BBANDS(
                name=f"{self.name}_bbands",
                source="close",
                period=self.bb_length,
                std=self.bb_std,
            )
        )
        self.sub_kc = self.add_child(
            KC(
                name=f"{self.name}_kc",
                source="close",
                period=self.kc_length,
                multiplier=self.kc_scalar,
                mamode="sma",
            )
        )
        smoothing_indicator: SMA | EMA
        if self.mamode == "ema":
            smoothing_indicator = EMA(
                name=f"{self.name}_momentum_ema",
                source=self._momentum.managed,
                period=self.mom_smooth,
            )
        else:
            smoothing_indicator = SMA(
                name=f"{self.name}_momentum_sma",
                source=self._momentum.managed,
                period=self.mom_smooth,
            )
        self.sub_momentum_ma = self.add_child_managed(smoothing_indicator)

    def _calculate_reading(self, index: int) -> dict[str, float | int | None]:
        squeeze = None
        if self.reading_period(self.mom_length + 1, "close", index):
            squeeze = self.close - self.at_src(index - self.mom_length)

        self._momentum.set(squeeze)
        self.sub_momentum_ma.calculate_index(index)

        smoothed_momentum = self.sub_momentum_ma.reading()
        bbands = self.sub_bbands.reading()
        kc = self.sub_kc.reading()

        if bbands is None or kc is None:
            return {"SQZ": smoothed_momentum, "ON": 0, "OFF": 0}

        bb_lower = bbands["BBL"]
        bb_upper = bbands["BBU"]
        kc_lower = kc["lower"]
        kc_upper = kc["upper"]

        if bb_lower is None or bb_upper is None or kc_lower is None or kc_upper is None:
            return {"SQZ": smoothed_momentum, "ON": 0, "OFF": 0}

        return {
            "SQZ": smoothed_momentum,
            "ON": int(bb_lower > kc_lower and bb_upper < kc_upper),
            "OFF": int(bb_lower < kc_lower and bb_upper > kc_upper),
        }
