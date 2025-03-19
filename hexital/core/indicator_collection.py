from collections.abc import Sequence
from dataclasses import dataclass

from hexital.core.indicator import Indicator


@dataclass
class IndicatorCollection:
    def collection_list(self) -> Sequence[Indicator]:
        return [f for f in vars(self).values() if isinstance(f, Indicator)]
