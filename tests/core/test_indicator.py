from dataclasses import dataclass, field
from datetime import datetime, timedelta

import pytest
from hexital import Candle
from hexital.analysis.patterns import doji
from hexital.candlesticks.heikinashi import HeikinAshi
from hexital.core.indicator import ChildWhen, Indicator
from hexital.exceptions import InvalidCandlestickType
from hexital.indicators.amorph import Amorph
from hexital.utils import timeframe


@dataclass(kw_only=True)
class FakeIndicator(Indicator):
    _name: str = field(init=False, default="Fake")
    period: int = 10
    source: str = "close"

    def _calculate_reading(self, index: int) -> float | dict | None:
        return 100.0


def test_calculate(minimal_candles: list[Candle]):
    test = FakeIndicator(candles=minimal_candles)
    test.calculate()
    assert minimal_candles[-1].indicators.get("Fake_10")


def test_name_default(minimal_candles: list[Candle]):
    test = FakeIndicator(candles=minimal_candles)
    test.calculate()
    assert test.reading("Fake_10")
    assert test.name == "Fake_10"


def test_name_default_timeframe_inherit(minimal_candles: list[Candle]):
    test = FakeIndicator(timeframe=timeframe.TimeFrame.MINUTE)
    test.append(minimal_candles)
    test.calculate()
    assert test.reading("Fake_10_T1")
    assert test.name == "Fake_10_T1"


def test_unlabeled_candles_skipped_by_resample_manager(
    minimal_candles_untimeframed: list[Candle],
):
    test = FakeIndicator(timeframe=timeframe.TimeFrame.MINUTE)
    test.append(minimal_candles_untimeframed)
    test.calculate()
    assert len(test.candles) == 0


def test_name_override(minimal_candles: list[Candle]):
    test = FakeIndicator(candles=minimal_candles, name="FUCK")
    test.calculate()
    assert test.name == "FUCK"


def test_name_timeframe(minimal_candles: list[Candle]):
    test = FakeIndicator(candles=minimal_candles, timeframe="t5")
    test.calculate()
    assert test.name == "Fake_10_T5"


def test_name_timeframe_override(minimal_candles: list[Candle]):
    test = FakeIndicator(candles=minimal_candles, name="FUCK", timeframe="t5")
    test.calculate()
    assert test.name == "FUCK"


def test_read(minimal_candles: list[Candle]):
    test = FakeIndicator(candles=minimal_candles)
    assert test.reading() is None
    test.calculate()
    assert test.reading() == 100.0


def test_set_reading(minimal_candles: list[Candle]):
    test = FakeIndicator(candles=minimal_candles)
    test.calculate()
    assert test.reading() == 100
    test._set_reading(420)
    assert test.reading() == 420


def test_set_reading_indexed(minimal_candles: list[Candle]):
    test = FakeIndicator(candles=minimal_candles)
    test.calculate()
    assert test.prev_reading() == 100
    test._set_reading(420, -2)
    assert test.prev_reading() == 420


def test_reading_period(minimal_candles: list[Candle]):
    test = FakeIndicator(candles=minimal_candles)
    assert test.reading_period(10) is False
    test.calculate()
    assert test.reading_period(10) is True


class TestSettings:
    def test_settings(self):
        test = FakeIndicator(candles=[])
        assert test.settings == {
            "name": "Fake_10",
            "rounding": 4,
            "source": "close",
            "period": 10,
        }

    def test_settings_timeframe(self):
        test = FakeIndicator(candles=[], timeframe="T5")
        assert test.settings == {
            "name": "Fake_10_T5",
            "rounding": 4,
            "source": "close",
            "period": 10,
            "timeframe": "T5",
            "timeframe_fill": False,
        }

    def test_settings_candlestick_types(self):
        test = FakeIndicator(candles=[], candlestick="HA")
        assert test.settings == {
            "name": "Fake_10",
            "rounding": 4,
            "source": "close",
            "period": 10,
            "candlestick": "HA",
        }

    def test_settings_back(self):
        as_dict = {
            "name": "Fake_10",
            "rounding": 4,
            "source": "close",
            "period": 10,
            "timeframe": "T5",
            "timeframe_fill": False,
            "candlestick": "HA",
        }
        test = FakeIndicator(**as_dict)

        assert test.settings == as_dict

    def test_settings_analysis(self):
        test = Amorph(analysis=doji, lookback=20)
        assert test.settings == {
            "analysis": "doji",
            "args": {"lookback": 20},
            "name": "doji",
            "rounding": 4,
        }


def test_purge(minimal_candles: list[Candle]):
    test = FakeIndicator(candles=minimal_candles)
    assert test.exists() is False
    test.calculate()
    assert test.exists() is True
    test.purge()
    assert test.exists() is False


def test_candle_timerange(minimal_candles):
    test = FakeIndicator(candles=[], candle_life=timedelta(minutes=1))

    test.append(minimal_candles)

    assert test.candles == [
        Candle(
            open=16346,
            high=4309,
            low=1903,
            close=6255,
            volume=31307,
            indicators={
                "Fake_10": 100.0,
            },
            timestamp=datetime(2023, 6, 1, 9, 18),
        ),
        Candle(
            open=2424,
            high=10767,
            low=13115,
            close=13649,
            volume=15750,
            indicators={
                "Fake_10": 100.0,
            },
            timestamp=datetime(2023, 6, 1, 9, 19),
        ),
    ]


def test_reading_as_list_exp(minimal_candles: list[Candle]):
    test_indicator = FakeIndicator(candles=minimal_candles)
    assert test_indicator.series("ATR") == [
        100,
        200,
        300,
        400,
        500,
        600,
        700,
        800,
        900,
        1000,
        1100,
        1200,
        1300,
        1400,
        1500,
        1600,
        1700,
        1800,
        1900,
        2000,
    ]


def test_reading_as_list_partial(minimal_candles: list[Candle]):
    test_indicator = FakeIndicator(candles=minimal_candles)
    assert test_indicator.series("MinTR") == [
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        None,
        1102,
        1202,
        1302,
        1402,
        1502,
        1602,
        1702,
        1802,
        1902,
        2002,
    ]


def test_reading_as_list_no_indicator(minimal_candles: list[Candle]):
    test_indicator = FakeIndicator(candles=minimal_candles)
    assert test_indicator.series("FUCK") == [None] * 20


class TestCandlestickType:
    def test_indicator_candlestick_type(self):
        test_indicator = FakeIndicator(candles=[], candlestick=HeikinAshi())
        assert isinstance(test_indicator.candlestick, HeikinAshi)

    def test_indicator_candlestick_type_str(self):
        test_indicator = FakeIndicator(candles=[], candlestick="HA")
        assert isinstance(test_indicator.candlestick, HeikinAshi)

    def test_indicator_candlestick_type_error(self):
        with pytest.raises(InvalidCandlestickType):
            test_indicator = FakeIndicator(candles=[], candlestick="FUCK")


@dataclass(kw_only=True)
class _ChildIndicator(Indicator[float | None]):
    _name: str = field(init=False, default="Child")
    value: float = 0.0

    def _generate_name(self):
        self.name = self._name
        self._refresh_fingerprint()

    def _calculate_reading(self, index: int) -> float | None:
        return self.value + index


class TestAddChild:
    def test_add_child_before(self, minimal_candles: list[Candle]):
        parent = FakeIndicator(candles=minimal_candles)
        child = parent.add_child(_ChildIndicator(value=10.0))
        parent.calculate()

        assert child.name == "Child"
        assert child._when == ChildWhen.BEFORE
        assert child.reading() == 10.0 + (len(minimal_candles) - 1)

    def test_add_child_dedup_returns_existing(self, minimal_candles: list[Candle]):
        from hexital.indicators.ema import EMA

        parent = FakeIndicator(candles=minimal_candles)
        first = parent.add_child(EMA(period=5))
        second = parent.add_child(EMA(period=5))

        assert first is second
        assert first.name == "EMA_5"
        children = list(parent.children.get_children(parent.fingerprint))
        assert len(children) == 1

    def test_add_child_shares_across_parents(self, minimal_candles: list[Candle]):
        from hexital.core.candle_manager import CandleManager
        from hexital.indicators.ema import EMA

        manager = CandleManager(minimal_candles)
        parent_a = FakeIndicator(candles=minimal_candles)
        parent_a.candle_manager = manager
        parent_b = FakeIndicator(candles=minimal_candles)
        parent_b.candle_manager = manager

        ema_a = parent_a.add_child(EMA(period=10))
        ema_b = parent_b.add_child(EMA(period=10))

        assert ema_a is ema_b
        assert parent_a.children is parent_b.children
        assert len(list(parent_a.children.get_children(parent_a.fingerprint))) == 1
        assert len(list(parent_b.children.get_children(parent_b.fingerprint))) == 1

    def test_purge_one_parent_keeps_shared_child(self, minimal_candles: list[Candle]):
        from hexital.core.candle_manager import CandleManager
        from hexital.indicators.ema import EMA

        manager = CandleManager(minimal_candles)
        parent_a = FakeIndicator(candles=minimal_candles, name="ParentA")
        parent_a.candle_manager = manager
        parent_b = FakeIndicator(candles=minimal_candles, name="ParentB")
        parent_b.candle_manager = manager

        ema = parent_a.add_child(EMA(period=10))
        parent_b.add_child(EMA(period=10))
        parent_a.calculate()

        assert ema.exists()
        parent_a.purge()
        assert ema.exists()

    def test_add_child_after(self, minimal_candles: list[Candle]):
        parent = FakeIndicator(candles=minimal_candles)
        child = parent.add_child_after(_ChildIndicator(value=5.0))
        parent.calculate()

        assert child._when == ChildWhen.AFTER
        assert child.reading() == 5.0 + (len(minimal_candles) - 1)


class TestAddState:
    def test_add_state_registers_managed_child(self, minimal_candles: list[Candle]):
        parent = FakeIndicator(candles=minimal_candles)
        state = parent.add_state()
        parent.calculate()

        assert state.managed.name == f"{parent.name}_data"
        assert state.managed._when == ChildWhen.MANUAL

    def test_add_state_custom_name(self, minimal_candles: list[Candle]):
        parent = FakeIndicator(candles=minimal_candles)
        state = parent.add_state(name=f"{parent.name}_macd")
        parent.calculate()

        assert state.managed.name == f"{parent.name}_macd"

    def test_state_set_and_update(self, minimal_candles: list[Candle]):
        parent = FakeIndicator(candles=minimal_candles)
        state = parent.add_state()
        parent.calculate()

        state.set({"gain": 1.0, "loss": 2.0})
        assert state.reading() == {"gain": 1.0, "loss": 2.0}

        state.update(gain=3.0)
        assert state.reading() == {"gain": 3.0, "loss": 2.0}

    def test_state_set_and_update_indexed(self, minimal_candles: list[Candle]):
        parent = FakeIndicator(candles=minimal_candles)
        state = parent.add_state()
        parent.calculate()

        state.set({"gain": 1.0}, index=-2)
        state.update(-2, loss=2.0)

        assert parent.reading(state.managed, index=-2) == {"gain": 1.0, "loss": 2.0}

    def test_state_prev_and_source(self, minimal_candles: list[Candle]):
        parent = FakeIndicator(candles=minimal_candles)
        state = parent.add_state()
        parent.calculate()

        state.managed.set_reading({"value": 10.0}, index=-2)
        state.managed.set_reading({"value": 20.0}, index=-1)

        assert state.prev("value") == 10.0
        assert state.reading("value") == 20.0
        assert state.source("value").name == f"{state.managed.name}:value"
        assert state.source("value") is state.source("value")


class TestCandleTimeframeLabel:
    def test_labeled_candles_do_not_enable_resampling(
        self, minimal_candles: list[Candle]
    ):
        indicator = FakeIndicator(candles=minimal_candles)
        indicator.calculate()

        assert indicator.timeframe is None
        assert indicator.name == "Fake_10"
        assert len(indicator.candles) == len(minimal_candles)

    def test_explicit_indicator_timeframe_resamples(
        self, minimal_candles_untimeframed: list[Candle]
    ):
        indicator = FakeIndicator(
            candles=minimal_candles_untimeframed, timeframe=timeframe.TimeFrame.MINUTE
        )
        indicator.calculate()

        assert indicator.name == "Fake_10_T1"
        assert len(indicator.candles) < len(minimal_candles_untimeframed)


class TestAuthorShortcuts:
    def test_ohlcv_properties(self, minimal_candles: list[Candle]):
        parent = FakeIndicator(candles=minimal_candles)
        parent.calculate()

        assert parent.close == minimal_candles[-1].close
        assert parent.open == minimal_candles[-1].open
        assert parent.at(-2, "high") == minimal_candles[-2].high

    def test_prev_alias(self, minimal_candles: list[Candle]):
        parent = FakeIndicator(candles=minimal_candles)
        parent.calculate()

        assert parent.prev() == 100.0
        assert parent.prev("close") == minimal_candles[-2].close

    def test_src_shortcuts(self, minimal_candles: list[Candle]):
        parent = FakeIndicator(candles=minimal_candles, source="close")
        parent.calculate()

        assert parent.src() == parent.close
        assert parent.prev_src() == minimal_candles[-2].close


class TestIndicatorNaming:
    def test_default_generate_name(self):
        from hexital.indicators.sma import SMA

        assert SMA(period=10).name == "SMA_10"

    def test_default_generate_name_includes_source(self):
        from hexital.indicators.ema import EMA

        assert EMA(period=10, source="close").name == "EMA_10"

    def test_default_generate_name_includes_non_ohlc_source(self):
        from hexital.indicators.hlca import HLCA
        from hexital.indicators.sma import SMA

        hlca = HLCA()
        assert SMA(period=10, source=hlca).name == "SMA_10_HLCA"

    def test_generate_fingerprint_is_stable_on_shared_manager(self):
        from hexital.indicators.sma import SMA

        first = SMA(period=10)
        second = SMA(period=10)
        second.candle_manager = first.candle_manager
        second._refresh_fingerprint()

        assert first.fingerprint == second.fingerprint
        assert len(first.fingerprint) == 64

    def test_generate_fingerprint_differs_by_manager(self):
        from hexital.indicators.sma import SMA

        assert SMA(period=10).fingerprint != SMA(period=10).fingerprint

    def test_generate_fingerprint_differs_by_period(self):
        from hexital.indicators.sma import SMA

        assert SMA(period=10).fingerprint != SMA(period=20).fingerprint

    def test_generate_fingerprint_differs_by_when(self, minimal_candles: list[Candle]):
        from hexital.indicators.ema import EMA

        parent = FakeIndicator(candles=minimal_candles)
        before = parent.add_child(EMA(period=5))
        after = parent.add_child_after(EMA(period=5))
        assert before.fingerprint != after.fingerprint

    def test_explicit_name_override_keeps_custom_fingerprint(self):
        indicator = FakeIndicator(candles=[], name="CUSTOM")
        assert indicator.name == "CUSTOM"
        assert indicator.fingerprint
