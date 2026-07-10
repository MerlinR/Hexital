from dataclasses import dataclass, field

from ..core.indicator import Indicator
from ..exceptions import InvalidIndicator
from .bbands import BBANDS
from .ema import EMA
from .kc import KC
from .sma import SMA


@dataclass(kw_only=True)
class SqueezePro(Indicator[dict[str, float | int | None]]):
    """SqueezePro

    Squeeze Pro extends the classic squeeze by comparing Bollinger Bands against
    three Keltner Channel widths while keeping the same momentum oscillator.

    Output type: `Dict["SQZ": float, "Wide": int, "Normal": int, "Narrow": int, "OFF": int]`
    """

    _name: str = field(init=False, default="SQPRO")
    bb_length: int = 20
    bb_std: float = 2.0
    kc_length: int = 20
    kc_scalar_wide: float = 2.0
    kc_scalar_normal: float = 1.5
    kc_scalar_narrow: float = 1.0
    mom_length: int = 12
    mom_smooth: int = 6
    mamode: str = "sma"

    def _name_parts(self) -> list[str]:
        return [
            "bb_length",
            "bb_std",
            "kc_length",
            "kc_scalar_wide",
            "kc_scalar_normal",
            "kc_scalar_narrow",
        ]

    def _validate_fields(self):
        self.mamode = self.mamode.lower()
        if self.mamode not in {"sma", "ema"}:
            raise InvalidIndicator(
                f"Invalid mamode {self.mamode!r}; expected 'sma' or 'ema'"
            )

        if not (self.kc_scalar_wide > self.kc_scalar_normal > self.kc_scalar_narrow):
            raise InvalidIndicator(
                "kc_scalar_wide must be greater than kc_scalar_normal, "
                "and kc_scalar_normal must be greater than kc_scalar_narrow"
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
        self.sub_kc_wide = self.add_child(
            KC(
                name=f"{self.name}_kc_wide",
                source="close",
                period=self.kc_length,
                multiplier=self.kc_scalar_wide,
                mamode=self.mamode,
                tr=True,
            )
        )
        self.sub_kc_normal = self.add_child(
            KC(
                name=f"{self.name}_kc_normal",
                source="close",
                period=self.kc_length,
                multiplier=self.kc_scalar_normal,
                mamode=self.mamode,
                tr=True,
            )
        )
        self.sub_kc_narrow = self.add_child(
            KC(
                name=f"{self.name}_kc_narrow",
                source="close",
                period=self.kc_length,
                multiplier=self.kc_scalar_narrow,
                mamode=self.mamode,
                tr=True,
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

        momentum = self.sub_momentum_ma.reading()
        bbands = self.sub_bbands.reading()
        kc_wide = self.sub_kc_wide.reading()
        kc_normal = self.sub_kc_normal.reading()
        kc_narrow = self.sub_kc_narrow.reading()

        if bbands is None or kc_wide is None or kc_normal is None or kc_narrow is None:
            return {"SQZ": momentum, "Wide": 0, "Normal": 0, "Narrow": 0, "OFF": 0}

        bb_lower = bbands["BBL"]
        bb_upper = bbands["BBU"]
        wide_lower = kc_wide["lower"]
        wide_upper = kc_wide["upper"]
        normal_lower = kc_normal["lower"]
        normal_upper = kc_normal["upper"]
        narrow_lower = kc_narrow["lower"]
        narrow_upper = kc_narrow["upper"]

        if (
            bb_lower is None
            or bb_upper is None
            or wide_lower is None
            or wide_upper is None
            or normal_lower is None
            or normal_upper is None
            or narrow_lower is None
            or narrow_upper is None
        ):
            return {"SQZ": momentum, "Wide": 0, "Normal": 0, "Narrow": 0, "OFF": 0}

        return {
            "SQZ": momentum,
            "Wide": int(bb_lower > wide_lower and bb_upper < wide_upper),
            "Normal": int(bb_lower > normal_lower and bb_upper < normal_upper),
            "Narrow": int(bb_lower > narrow_lower and bb_upper < narrow_upper),
            "OFF": int(bb_lower < wide_lower and bb_upper > wide_upper),
        }
