import importlib
import inspect
from copy import deepcopy
from typing import Callable, Optional

from hexital.core import Indicator
from hexital.exceptions import InvalidAnalysis


class Amorph(Indicator):
    """Amorph

    Flexible Skeleton Indicator that will use a method
    to generate readings on every Candle like indicators.
    The given Method is expected to have 'candles' and 'index' as named arguments

    Arguments:
    All of Indicator Arguments and All of the given Amorph Arguments as keyword arguments
    or use args as a dict of keyword arguments for called analysis

    """

    _analysis_method: Callable
    _analysis_kwargs: dict

    def __init__(self, analysis: str | Callable, args: Optional[dict] = None, **kwargs):
        if isinstance(analysis, str):
            pattern_module = importlib.import_module("hexital.analysis.patterns")
            movement_module = importlib.import_module("hexital.analysis.movement")
            pattern_method = getattr(pattern_module, analysis, None)
            analysis_func = getattr(movement_module, analysis, pattern_method)

            if analysis_func is not None:
                self._analysis_method = analysis_func

        elif callable(analysis):
            self._analysis_method = analysis

        if not hasattr(self, "_analysis_method"):
            raise InvalidAnalysis(f"The given analysis [{analysis}] is invalid")

        self._analysis_kwargs, kwargs = self._seperate_indicator_attributes(kwargs)

        if isinstance(args, dict):
            self._analysis_kwargs.update(args)

        super().__init__(**kwargs)

    @property
    def settings(self) -> dict:
        """Returns a dict format of how this indicator can be generated"""
        settings = self.__dict__
        output = {"analysis": self._analysis_method.__name__}

        for name, value in settings.items():
            if name == "candles":
                continue
            if name == "timeframe_fill" and self.timeframe is None:
                continue
            if not name.startswith("_") and value:
                output[name] = deepcopy(value)

        return output

    @staticmethod
    def _seperate_indicator_attributes(kwargs: dict) -> tuple[dict, dict]:
        indicator_attr = inspect.getmembers(Indicator)[1][1].keys()
        analysis_args = {}
        for argum in list(kwargs.keys()):
            if argum not in indicator_attr:
                analysis_args[argum] = kwargs.pop(argum)

        return analysis_args, kwargs

    def _generate_name(self) -> str:
        name = self._analysis_method.__name__
        if self._analysis_kwargs.get("length"):
            name += f"_{self._analysis_kwargs['length']}"
        return name

    def _calculate_reading(self, index: int) -> float | dict | None:
        return self._analysis_method(candles=self.candles, index=index, **self._analysis_kwargs)
