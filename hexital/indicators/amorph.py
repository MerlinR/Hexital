import inspect
from copy import deepcopy
from typing import Callable, Optional

from hexital.core.indicator import Indicator


class Amorph(Indicator):
    """Amorph

    Flexible Skeleton Indicator that will use a method
    to generate readings on every Candle like indicators.

    The given Method is expected to have 'candles' and 'index' as named arguments, EG:

    Input type Example: [Doji][hexital.analysis.patterns.doji]

    Output type: Based on analysis method

    Args:
        analysis: Period to index back in
        args: All of the Arguments as keyword arguments as a dict of keyword arguments for called analysis
    """

    _analysis_method: Callable
    _analysis_kwargs: dict

    def __init__(self, analysis: Callable, args: Optional[dict] = None, **kwargs):
        self._analysis_method = analysis
        self._analysis_kwargs, kwargs = self._separate_indicator_attributes(kwargs)

        if isinstance(args, dict):
            self._analysis_kwargs.update(args)

        super().__init__(**kwargs)

    @property
    def settings(self) -> dict:
        """Returns a dict format of how this indicator can be generated"""
        output = {"analysis": self._analysis_method.__name__}

        for name, value in self.__dict__.items():
            if name == "candles":
                continue
            if name == "timeframe_fill" and self.timeframe is None:
                continue
            if not name.startswith("_") and value:
                output[name] = deepcopy(value)

        return output

    @staticmethod
    def _separate_indicator_attributes(kwargs: dict) -> tuple[dict, dict]:
        indicator_attr = inspect.getmembers(Indicator)[1][1].keys()
        analysis_args = {}
        for argum in list(kwargs.keys()):
            if argum not in indicator_attr:
                analysis_args[argum] = kwargs.pop(argum)

        return analysis_args, kwargs

    def _generate_name(self) -> str:
        name = self._analysis_method.__name__
        period = self._analysis_kwargs.get("period")
        return f"{name}_{period}" if period else name

    def _calculate_reading(self, index: int) -> float | dict | None:
        return self._analysis_method(candles=self.candles, index=index, **self._analysis_kwargs)
