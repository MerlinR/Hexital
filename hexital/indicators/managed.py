from dataclasses import dataclass
from typing import Union

from hexital.types import Indicator


@dataclass(kw_only=True)
class Managed(Indicator):
    """Managed

    Empty Indicator thats manually controlled and the reading manually set.

    """

    indicator_name: str = "MAN"
    _sub_indicator: bool = True

    def _generate_name(self) -> str:
        return self.indicator_name

    def set_reading(self, index: int, reading: Union[float, dict]):
        self._set_reading(index, reading)
