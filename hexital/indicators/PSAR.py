from dataclasses import dataclass, field

from ..core.indicator import Indicator


@dataclass(kw_only=True)
class PSAR(Indicator[dict[str, float | int | None]]):
    """Parabolic Stop And Reverse - PSAR

    PSAR is a trend-following indicator that trails price using an acceleration
    factor and reverses when price crosses the active stop level.

    Output type: `Dict["Long": float, "Short": float, "Acceleration": float, "Reversal": int]`

    Args:
        acc_factor (float): Initial acceleration factor. Defaults to 0.02
        max_af (float): Maximum acceleration factor. Defaults to 0.2
    """

    _name: str = field(init=False, default="PSAR")
    acc_factor: float = 0.02
    max_af: float = 0.2

    def _generate_name(self) -> str:
        return self._name

    def _initialise(self):
        self._state = self.add_state(name=f"{self.name}_state")

    def _is_falling(self) -> bool:
        if len(self.candles) < 2:
            return False

        up = self.candles[1].high - self.candles[0].high
        down = self.candles[0].low - self.candles[1].low
        return down > up and down > 0

    def _calculate_reading(self, index: int) -> dict[str, float | int | None]:
        if index == 0:
            falling = self._is_falling()
            sar = self.high if falling else self.low
            ep = self.low if falling else self.high
            self._state.set(
                {
                    "sar": sar,
                    "ep": ep,
                    "af": self.acc_factor,
                    "falling": falling,
                }
            )
            return {
                "Long": None,
                "Short": None,
                "Acceleration": self.acc_factor,
                "Reversal": 0,
            }

        state = self._state.prev(default={})
        sar = state.get("sar")
        ep = state.get("ep")
        af = state.get("af", self.acc_factor)
        falling = state.get("falling", False)

        if sar is None or ep is None:
            return {"Long": None, "Short": None, "Acceleration": af, "Reversal": 0}

        sar = sar + (af * (ep - sar))
        raw_sar = sar
        reversal = 0

        prev_high = self.candles[index - 1].high
        prev_low = self.candles[index - 1].low
        prev2_high = self.candles[index - 2].high if index > 1 else prev_high
        prev2_low = self.candles[index - 2].low if index > 1 else prev_low

        if falling:
            if self.high > raw_sar:
                reversal = 1
                falling = False
                sar = ep
                ep = self.high
                af = self.acc_factor
            else:
                sar = max(sar, prev_high, prev2_high)
                if self.low < ep:
                    ep = self.low
                    af = min(af + self.acc_factor, self.max_af)
        else:
            if self.low < raw_sar:
                reversal = 1
                falling = True
                sar = ep
                ep = self.low
                af = self.acc_factor
            else:
                sar = min(sar, prev_low, prev2_low)
                if self.high > ep:
                    ep = self.high
                    af = min(af + self.acc_factor, self.max_af)

        self._state.set(
            {
                "sar": sar,
                "ep": ep,
                "af": af,
                "falling": falling,
            }
        )

        return {
            "Long": None if falling else sar,
            "Short": sar if falling else None,
            "Acceleration": af,
            "Reversal": reversal,
        }
