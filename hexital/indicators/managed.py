from dataclasses import dataclass
from typing import Optional, Union

from hexital.core import Indicator


@dataclass(kw_only=True)
class Managed(Indicator):
    """Managed

    Empty Indicator thats manually controlled and the reading manually set.

    """

    indicator_name: str = "MAN"
    _sub_indicator: bool = True
    _active_index: int = 0

    def _generate_name(self) -> str:
        return self.indicator_name

    def set_reading(self, reading: Union[float, dict], index: Optional[int] = None):
        if index is None:
            index = self._active_index
        else:
            self.set_active_index(index)
        self._set_reading(reading, self._active_index)

    def set_active_index(self, index: int):
        self._active_index = index
