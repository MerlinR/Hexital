import importlib
import inspect
from copy import deepcopy
from typing import Callable

from hexital.core import Indicator
from hexital.exceptions import InvalidPattern


class Pattern(Indicator):
    """Pattern

    Flexible Skeleton Indicator that will use candle Analysis patterns
    to generate pattern results on every Candle like indicators.

    Arguments:
    All of Indicator Arguments and All of the given Pattern Arguments as keyword arguments
    or use args as a dict of keyword arguments for called pattern

    """

    _pattern_method: Callable = None
    _pattern_kwargs = {}

    def __init__(self, pattern: str | Callable, args: dict = None, **kwargs):
        if isinstance(pattern, str):
            pattern_module = importlib.import_module("hexital.analysis.patterns")
            pattern_method = getattr(pattern_module, pattern, None)
            if pattern_method is not None:
                self._pattern_method = pattern_method
        elif callable(pattern):
            self._pattern_method = pattern

        if self._pattern_method is None:
            raise InvalidPattern(f"The given pattern [{pattern}] is invalid")

        self._pattern_kwargs, kwargs = self._seperate_indicator_attributes(kwargs)

        if isinstance(args, dict):
            self._pattern_kwargs.update(args)

        super().__init__(**kwargs)

    @property
    def settings(self) -> dict:
        """Returns a dict format of how this indicator can be generated"""
        settings = self.__dict__
        output = {"pattern": self._pattern_method.__name__}

        for name, value in settings.items():
            if name == "candles":
                continue
            if name == "timeframe_fill" and self.timeframe is None:
                continue
            if not name.startswith("_") and value is not None:
                output[name] = deepcopy(value)

        return output

    @staticmethod
    def _seperate_indicator_attributes(kwargs: dict) -> tuple[dict, dict]:
        indicator_attr = inspect.getmembers(Indicator)[1][1].keys()
        pattern_args = {}
        for argum in list(kwargs.keys()):
            if argum not in indicator_attr:
                pattern_args[argum] = kwargs.pop(argum)

        return pattern_args, kwargs

    def _generate_name(self) -> str:
        name = self._pattern_method.__name__
        if self._pattern_kwargs.get("length"):
            name += f"_{self._pattern_kwargs['length']}"
        return name

    def _calculate_reading(self, index: int) -> float | dict | None:
        return self._pattern_method(
            candles=self.candles, index=index, **self._pattern_kwargs
        )
