from dataclasses import dataclass

from hexital.core import Indicator


@dataclass(kw_only=True)
class OBV(Indicator):
    """On-Balance Volume

    Sources:
       https://www.investopedia.com/terms/o/onbalancevolume.asp

    """

    indicator_name: str = "OBV"

    def _generate_name(self) -> str:
        return self.indicator_name

    def _calculate_reading(self, index: int) -> float | dict | None:
        if self.prev_exists():
            if self.reading("volume") == self.prev_reading("volume"):
                return self.prev_reading()
            elif self.reading("close") > self.prev_reading("close"):
                return self.prev_reading() + self.reading("volume")

            return self.prev_reading() - self.reading("volume")

        return self.reading("volume")
