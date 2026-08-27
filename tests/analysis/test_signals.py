from hexital.analysis import (
    all_of,
    any_of,
    between_values,
    crossover_level,
    crossunder_level,
    edge,
    falling_edge,
    level_edge,
    level_falling_edge,
    none_of,
)
from hexital.analysis.signals import crossed_above, crossed_below


class TestSignals:
    def test_edge(self):
        assert edge(True, False) is True
        assert edge(True, True) is False
        assert edge(True, None) is True
        assert edge(False, False) is False
        assert edge(None, False) is False

    def test_falling_edge(self):
        assert falling_edge(False, True) is True
        assert falling_edge(True, True) is False
        assert falling_edge(False, None) is False
        assert falling_edge(None, True) is True

    def test_level_edge(self):
        assert level_edge(True, False) is True
        assert level_edge(True, True) is False

    def test_level_falling_edge(self):
        assert level_falling_edge(False, True) is True
        assert level_falling_edge(True, True) is False

    def test_crossed_above(self):
        assert crossed_above(31, 29, 30) is True
        assert crossed_above(30, 29, 30) is False
        assert crossed_above(31, None, 30) is False

    def test_crossed_below(self):
        assert crossed_below(29, 31, 30) is True
        assert crossed_below(30, 31, 30) is False
        assert crossed_below(29, None, 30) is False

    def test_between(self):
        assert between_values(30, 20, 40) is True
        assert between_values(20, 20, 40) is True
        assert between_values(41, 20, 40) is False
        assert between_values(None, 20, 40) is False

    def test_all_of(self):
        assert all_of(True, True) is True
        assert all_of(True, False) is False
        assert all_of(True, None) is False
        assert all_of() is False

    def test_any_of(self):
        assert any_of(False, True) is True
        assert any_of(False, None) is False
        assert any_of() is False

    def test_none_of(self):
        assert none_of(False, False) is True
        assert none_of(False, None) is True
        assert none_of(False, True) is False
        assert none_of() is True


class TestAnalysisExports:
    def test_crossover_level_exported(self):
        assert callable(crossover_level)
        assert callable(crossunder_level)

    def test_signal_helpers_exported(self):
        assert all_of(True) is True
        assert any_of(False, True) is True
        assert none_of(False) is True
        assert edge(True, False) is True
        assert falling_edge(False, True) is True
        assert level_edge(True, False) is True
        assert level_falling_edge(False, True) is True
        assert crossed_above(31, 29, 30) is True
        assert between_values(25, 20, 30) is True

