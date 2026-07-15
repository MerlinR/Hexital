from __future__ import annotations

from collections.abc import Sequence
from dataclasses import Field, field, fields, is_dataclass
from typing import Any

from .indicator import Indicator

_INDICATOR_METADATA_KEY = "hexital_indicator"


def indicator_field(
    *,
    default: Any = ...,
    default_factory: Any = ...,
    **kwargs: Any,
) -> Field:
    """Mark a dataclass field as a strategy indicator for IndicatorCollection."""
    metadata = {**kwargs.pop("metadata", {}), _INDICATOR_METADATA_KEY: True}
    field_kwargs = {"metadata": metadata, **kwargs}
    if default_factory is not ...:
        return field(default_factory=default_factory, **field_kwargs)
    if default is not ...:
        return field(default=default, **field_kwargs)
    return field(**field_kwargs)


class IndicatorCollection:
    """Group indicators for direct attribute access on a strategy collection.

    Subclass as a dataclass and mark indicator fields with `indicator_field()`,
    or pass indicators explicitly to `__init__`.
    """

    _explicit: tuple[Indicator, ...] | None

    def __init__(self, *indicators: Indicator) -> None:
        self._explicit = indicators or None

    def collection_list(self) -> Sequence[Indicator]:
        explicit = getattr(self, "_explicit", None)
        if explicit is not None:
            return explicit

        if not is_dataclass(self):
            raise TypeError(
                f"{type(self).__name__} must use indicator_field() on dataclass "
                "fields or pass indicators to IndicatorCollection.__init__()"
            )

        indicators: list[Indicator] = []
        for dataclass_field in fields(self):
            if not dataclass_field.metadata.get(_INDICATOR_METADATA_KEY):
                continue
            value = getattr(self, dataclass_field.name)
            if not isinstance(value, Indicator):
                raise TypeError(
                    f"{type(self).__name__}.{dataclass_field.name} must be an Indicator"
                )
            indicators.append(value)

        if not indicators:
            raise TypeError(
                f"{type(self).__name__} has no fields marked with indicator_field()"
            )

        return indicators
