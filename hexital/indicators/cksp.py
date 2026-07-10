from dataclasses import dataclass, field

from ..analysis import movement
from ..core.indicator import Indicator
from .atr import ATR
from .tr import TR


@dataclass(kw_only=True)
class CKSP(Indicator[dict[str, float | None]]):
    """Chande Kroll Stop - CKSP

    CKSP builds trailing stop bands from ATR and then smooths those raw stop
    levels with rolling extrema.

    Sources:
        https://tradingstrategy.ai/docs/api/technical-analysis/trend/help/pandas_ta.trend.cksp.html

    Output type: `Dict["long": float, "short": float]`

    Args:
        period (int): ATR and primary stop lookback. Defaults to 10.
            pandas_ta alias: ``p``
        multiplier (float): ATR multiplier. Defaults to 3.0.
            pandas_ta alias: ``x``
        smooth_period (int): Secondary smoothing lookback. Defaults to 20.
            pandas_ta alias: ``q``
        tvmode (bool): Use TradingView ATR smoothing mode. Defaults to True.
    """

    _name: str = field(init=False, default="CKSP")
    period: int = 10
    multiplier: float = 3.0
    smooth_period: int = 20
    tvmode: bool = True

    def _name_parts(self) -> list[str]:
        return ["period", "multiplier", "smooth_period"]

    def _initialise(self):
        self._raw = self.add_state(name=f"{self.name}_raw")

        if self.tvmode:
            self.sub_atr = self.add_child(ATR(period=self.period))
            self.sub_tr = None
        else:
            self.sub_atr = None
            self.sub_tr = self.add_child(TR())

    def _calculate_reading(self, index: int) -> dict[str, float | None]:
        atr_ = self._atr_reading(index)
        if atr_ is None:
            return {"long": None, "short": None}

        high_ = movement.highest(self.candles, "high", self.period, index)
        low_ = movement.lowest(self.candles, "low", self.period, index)
        if high_ is None or low_ is None:
            return {"long": None, "short": None}

        self._raw.set(
            {
                "long_raw": high_ - (self.multiplier * atr_),
                "short_raw": low_ + (self.multiplier * atr_),
            }
        )

        long_readings = self.get_readings_period(
            self.smooth_period,
            self._raw.source("long_raw"),
            index=index,
            include_latest=True,
        )
        short_readings = self.get_readings_period(
            self.smooth_period,
            self._raw.source("short_raw"),
            index=index,
            include_latest=True,
        )

        if (
            len(long_readings) < self.smooth_period
            or len(short_readings) < self.smooth_period
        ):
            return {"long": None, "short": None}

        return {
            "long": max(long_readings),
            "short": min(short_readings),
        }

    def _atr_reading(self, index: int) -> float | None:
        if self.sub_atr is not None:
            return self.sub_atr.reading()

        if self.sub_tr is None or not self.sub_tr.reading_period(
            self.period, index=index
        ):
            return None

        return self.sub_tr.candles_average(self.period, index=index)
