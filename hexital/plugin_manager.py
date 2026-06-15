from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from importlib import import_module
from importlib.metadata import entry_points
from typing import Any

from .exceptions import InvalidPlugin, PluginConflict

ENTRYPOINT_GROUP_INDICATORS = "hexital.indicators"
ENTRYPOINT_GROUP_ANALYSIS = "hexital.analysis"
ENTRYPOINT_GROUP_CANDLESTICKS = "hexital.candlesticks"


@dataclass
class PluginRegistry:
    indicators: dict[str, type[Any]] = field(default_factory=dict)
    analysis: dict[str, Callable[..., Any]] = field(default_factory=dict)
    candlesticks: dict[str, type[Any]] = field(default_factory=dict)


class PluginManager:
    builtins: PluginRegistry
    plugins: PluginRegistry
    _plugins_loaded: bool = False
    _builtins_loaded: bool = False

    def __init__(self):
        self.builtins = PluginRegistry()
        self.plugins = PluginRegistry()

    def _build_indicator_registry(self) -> dict[str, type[Any]]:
        indicators = import_module("hexital.indicators")
        indicator_module = import_module("hexital.core.indicator")
        indicator_base = indicator_module.Indicator
        registry: dict[str, type[Any]] = {}

        for name in indicators.__all__:
            value = getattr(indicators, name)
            if isinstance(value, type) and issubclass(value, indicator_base):
                registry[name] = value

        return registry

    def _build_analysis_registry(self) -> dict[str, Callable[..., Any]]:
        analysis = import_module("hexital.analysis")
        registry: dict[str, Callable[..., Any]] = {}

        for name in analysis.__all__:
            value = getattr(analysis, name)
            if callable(value):
                registry[name] = value

        return registry

    def _build_candlestick_registry(self) -> dict[str, type[Any]]:
        candlesticks = import_module("hexital.candlesticks")
        candlestick_module = import_module("hexital.core.candlestick_type")
        candlestick_base = candlestick_module.CandlestickType
        registry: dict[str, type[Any]] = {}

        for name in candlesticks.__all__:
            value = getattr(candlesticks, name)
            if (
                isinstance(value, type)
                and issubclass(value, candlestick_base)
                and value.acronym != "NA"
            ):
                registry[value.acronym] = value

        return registry

    def _ensure_builtins_loaded(self) -> None:
        if self._builtins_loaded:
            return

        self.builtins.indicators = self._build_indicator_registry()
        self.builtins.analysis = self._build_analysis_registry()
        self.builtins.candlesticks = self._build_candlestick_registry()
        self._builtins_loaded = True

    def _entry_points_for_group(self, group: str):
        return entry_points(group=group)

    def _check_conflict(
        self,
        name: str,
        existing: dict[str, Any],
        registry_type: str,
        allow_override: bool,
    ) -> None:
        if name in existing and not allow_override:
            raise PluginConflict(f"{registry_type} plugin name conflict: {name}")

    def register_indicator(
        self, name: str, indicator_class: type[Any], allow_override: bool = False
    ) -> None:
        self._ensure_builtins_loaded()
        indicator_module = import_module("hexital.core.indicator")
        indicator_base = indicator_module.Indicator

        if not isinstance(indicator_class, type) or not issubclass(
            indicator_class, indicator_base
        ):
            raise InvalidPlugin(f"Indicator plugin {name} must be an Indicator subclass")

        self._check_conflict(
            name,
            {**self.builtins.indicators, **self.plugins.indicators},
            "Indicator",
            allow_override=allow_override,
        )
        self.plugins.indicators[name] = indicator_class

    def register_analysis(
        self,
        name: str,
        analysis_method: Callable[..., Any],
        allow_override: bool = False,
    ) -> None:
        self._ensure_builtins_loaded()

        if not callable(analysis_method):
            raise InvalidPlugin(f"Analysis plugin {name} must be callable")

        self._check_conflict(
            name,
            {**self.builtins.analysis, **self.plugins.analysis},
            "Analysis",
            allow_override=allow_override,
        )
        self.plugins.analysis[name] = analysis_method

    def register_candlestick(
        self,
        name: str,
        candlestick_class: type[Any],
        allow_override: bool = False,
    ) -> None:
        self._ensure_builtins_loaded()
        candlestick_module = import_module("hexital.core.candlestick_type")
        candlestick_base = candlestick_module.CandlestickType

        if not isinstance(candlestick_class, type) or not issubclass(
            candlestick_class, candlestick_base
        ):
            raise InvalidPlugin(
                f"Candlestick plugin {name} must be a CandlestickType subclass"
            )

        self._check_conflict(
            name,
            {**self.builtins.candlesticks, **self.plugins.candlesticks},
            "Candlestick",
            allow_override=allow_override,
        )
        self.plugins.candlesticks[name] = candlestick_class

    def load_installed_plugins(self, force: bool = False) -> PluginRegistry:
        if self._plugins_loaded and not force:
            return self.plugins

        if force:
            self.plugins.indicators.clear()
            self.plugins.analysis.clear()
            self.plugins.candlesticks.clear()

        for ep in self._entry_points_for_group(ENTRYPOINT_GROUP_INDICATORS):
            self.register_indicator(ep.name, ep.load())

        for ep in self._entry_points_for_group(ENTRYPOINT_GROUP_ANALYSIS):
            self.register_analysis(ep.name, ep.load())

        for ep in self._entry_points_for_group(ENTRYPOINT_GROUP_CANDLESTICKS):
            self.register_candlestick(ep.name, ep.load())

        self._plugins_loaded = True
        return self.plugins

    def reset_plugins(self) -> None:
        self.plugins.indicators.clear()
        self.plugins.analysis.clear()
        self.plugins.candlesticks.clear()
        self._plugins_loaded = False

    def indicator_registry(self) -> dict[str, type[Any]]:
        self._ensure_builtins_loaded()
        return {**self.builtins.indicators, **self.plugins.indicators}

    def analysis_registry(self) -> dict[str, Callable[..., Any]]:
        self._ensure_builtins_loaded()
        return {**self.builtins.analysis, **self.plugins.analysis}

    def candlestick_registry(self) -> dict[str, type[Any]]:
        self._ensure_builtins_loaded()
        return {**self.builtins.candlesticks, **self.plugins.candlesticks}

    def get_indicator_class(self, name: str) -> type[Any] | None:
        return self.indicator_registry().get(name)

    def get_analysis(self, name: str) -> Callable[..., Any] | None:
        return self.analysis_registry().get(name)

    def get_candlestick_class(self, name: str) -> type[Any] | None:
        return self.candlestick_registry().get(name)


plugin_manager = PluginManager()


def load_installed_plugins(force: bool = False) -> PluginRegistry:
    return plugin_manager.load_installed_plugins(force=force)


def reset_plugins() -> None:
    plugin_manager.reset_plugins()


def register_indicator(
    name: str, indicator_class: type[Any], allow_override: bool = False
) -> None:
    plugin_manager.register_indicator(
        name, indicator_class, allow_override=allow_override
    )


def register_analysis(
    name: str,
    analysis_method: Callable[..., Any],
    allow_override: bool = False,
) -> None:
    plugin_manager.register_analysis(name, analysis_method, allow_override=allow_override)


def register_candlestick(
    name: str,
    candlestick_class: type[Any],
    allow_override: bool = False,
) -> None:
    plugin_manager.register_candlestick(
        name, candlestick_class, allow_override=allow_override
    )
