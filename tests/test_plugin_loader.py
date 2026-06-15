from __future__ import annotations

from dataclasses import dataclass, field

import hexital.core.hexital as hexital_core_module
import hexital.plugin_manager as plugin_loader_module
import pytest
from hexital import Candle, Hexital
from hexital.core.candlestick_type import CandlestickType
from hexital.core.indicator import Indicator
from hexital.exceptions import InvalidPlugin, PluginConflict
from hexital.plugin_manager import PluginManager


@dataclass(kw_only=True)
class PluginIndicator(Indicator):
    candles: list[Candle] = field(default_factory=list)
    _name: str = field(init=False, default="PluginIndicator")

    def _generate_name(self) -> str:
        return self._name

    def _calculate_reading(self, index: int) -> float | dict | None:
        return self.candles[index].close


class PluginCandlestick(CandlestickType):
    name = "Plugin Candlestick"
    acronym = "PLUG"

    def transform_candle(self, candle: Candle):
        return candle.clean_copy()


def plugin_analysis(candles: list[Candle], index: int = -1):
    return candles[index].close > candles[index].open


class FakeEntryPoint:
    def __init__(self, name, value):
        self.name = name
        self._value = value

    def load(self):
        return self._value


@pytest.fixture
def loader():
    return PluginManager()


def test_register_indicator_used_by_hexital(candles, loader, monkeypatch):
    loader.register_indicator("PluginIndicator", PluginIndicator)
    monkeypatch.setattr(plugin_loader_module, "plugin_manager", loader)
    monkeypatch.setattr(hexital_core_module, "plugin_manager", loader)

    strategy = Hexital("plugin", candles[:3], [{"indicator": "PluginIndicator"}])
    strategy.calculate()

    assert loader.get_indicator_class("PluginIndicator") is PluginIndicator
    assert strategy.indicator("PluginIndicator") is not None
    assert strategy.reading("PluginIndicator") == candles[2].close


def test_register_analysis_used_by_hexital(candles, loader, monkeypatch):
    loader.register_analysis("plugin_analysis", plugin_analysis)
    monkeypatch.setattr(plugin_loader_module, "plugin_manager", loader)
    monkeypatch.setattr(hexital_core_module, "plugin_manager", loader)

    strategy = Hexital("plugin", candles[:3], [{"analysis": "plugin_analysis"}])
    strategy.calculate()

    assert loader.get_analysis("plugin_analysis") is plugin_analysis
    assert strategy.reading("plugin_analysis") is plugin_analysis(candles[:3])


def test_register_candlestick_used_by_hexital(candles, loader, monkeypatch):
    loader.register_candlestick("PLUG", PluginCandlestick)
    monkeypatch.setattr(plugin_loader_module, "plugin_manager", loader)
    monkeypatch.setattr(hexital_core_module, "plugin_manager", loader)

    strategy = Hexital("plugin", candles[:3], candlestick="PLUG")

    assert loader.get_candlestick_class("PLUG") is PluginCandlestick
    assert strategy.candlestick is not None
    assert strategy.candlestick.acronym == "PLUG"


def test_register_indicator_conflict_raises(loader):
    with pytest.raises(PluginConflict):
        loader.register_indicator("EMA", PluginIndicator)


def test_register_invalid_analysis_raises(loader):
    with pytest.raises(InvalidPlugin):
        loader.register_analysis("bad", object())  # type: ignore[arg-type]


def test_load_installed_plugins(loader, monkeypatch):
    def fake_entry_points(*, group: str):
        if group == "hexital.indicators":
            return [FakeEntryPoint("PluginIndicator", PluginIndicator)]
        if group == "hexital.analysis":
            return [FakeEntryPoint("plugin_analysis", plugin_analysis)]
        if group == "hexital.candlesticks":
            return [FakeEntryPoint("PLUG", PluginCandlestick)]
        return []

    monkeypatch.setattr(plugin_loader_module, "entry_points", fake_entry_points)

    loader.load_installed_plugins()

    assert loader.get_indicator_class("PluginIndicator") is PluginIndicator
    assert loader.get_analysis("plugin_analysis") is plugin_analysis
    assert loader.get_candlestick_class("PLUG") is PluginCandlestick


def test_module_wrappers_delegate_to_default_loader(monkeypatch):
    loader = PluginManager()
    monkeypatch.setattr(plugin_loader_module, "plugin_manager", loader)

    plugin_loader_module.register_indicator("PluginIndicator", PluginIndicator)

    assert loader.get_indicator_class("PluginIndicator") is PluginIndicator
