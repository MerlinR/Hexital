from dataclasses import dataclass, field
from datetime import datetime, timedelta

import pytest

from hexital import Candle
from hexital.analysis.patterns import doji
from hexital.candlesticks.heikinashi import HeikinAshi
from hexital.core.indicator import ChildWhen, Indicator, Managed
from hexital.exceptions import InvalidCandlestickType, InvalidIndicator
from hexital.indicators import SMA
from hexital.indicators.amorph import Amorph
from hexital.indicators.dema import DEMA
from hexital.indicators.ema import EMA
from hexital.indicators.hlca import HLCA
from hexital.indicators.macd import MACD
from hexital.indicators.rsi import RSI
from hexital.utils import timeframe


@dataclass(kw_only=True)
class FakeIndicator(Indicator):
    _name: str = field(init=False, default="Fake")
    period: int = 10
    source: str = "close"

    def _minimum_candles(self) -> int:
        return self.period

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


def test_purge_nested_children(minimal_candles: list[Candle]):
    dema = DEMA(candles=minimal_candles)
    dema.calculate()

    names = dema._purge_names()
    assert dema.sub_ema2.name in names
    assert len(names) > len(dema.children) + 1

    candle = minimal_candles[-1]
    for name in names:
        assert name in candle.indicators or name in candle.sub_indicators

    dema.purge()

    for name in names:
        assert name not in candle.indicators
        assert name not in candle.sub_indicators


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

    def _generate_name(self) -> str:
        return self._name

    def _calculate_reading(self, index: int) -> float | None:
        return self.value + index


class TestAddChild:
    def test_add_child_before(self, minimal_candles: list[Candle]):
        parent = FakeIndicator(candles=minimal_candles)
        child = parent.add_child(_ChildIndicator(value=10.0))
        parent.calculate()

        assert child.name in parent.children
        assert child._when == ChildWhen.BEFORE
        assert child.reading() == 10.0 + (len(minimal_candles) - 1)

    def test_add_child_after(self, minimal_candles: list[Candle]):
        parent = FakeIndicator(candles=minimal_candles)
        child = parent.add_child_after(_ChildIndicator(value=5.0))
        parent.calculate()

        assert child._when == ChildWhen.AFTER
        assert child.reading() == 5.0 + (len(minimal_candles) - 1)

    def test_add_child_managed(self, minimal_candles: list[Candle]):
        parent = FakeIndicator(candles=minimal_candles)
        state = parent.add_child_managed(Managed())
        parent.calculate()

        assert state.name == f"{parent.name}_data"
        assert state._when == ChildWhen.MANUAL
        assert parent.children[state.name] is state
        state.set_reading({"x": 1})
        assert state.reading() == {"x": 1}

    def test_add_child_accepts_string_when(self, minimal_candles: list[Candle]):
        parent = FakeIndicator(candles=minimal_candles)
        child = parent.add_child(_ChildIndicator(), when="after")
        assert child._when == ChildWhen.AFTER

    def test_add_child_invalid_when(self, minimal_candles: list[Candle]):
        parent = FakeIndicator(candles=minimal_candles)
        with pytest.raises(InvalidIndicator, match="Invalid child when"):
            parent.add_child(_ChildIndicator(), when="invalid")


class TestAddState:
    def test_add_state_registers_managed_child(self, minimal_candles: list[Candle]):
        parent = FakeIndicator(candles=minimal_candles)
        state = parent.add_state()
        parent.calculate()

        assert state.managed.name == f"{parent.name}_data"
        assert state.managed._when == ChildWhen.MANUAL
        assert parent.children[state.managed.name] is state.managed

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
        assert SMA(period=10).name == "SMA_10"

    def test_default_generate_name_includes_source(self):
        assert EMA(period=10, source="close").name == "EMA_10"

    def test_default_generate_name_includes_non_ohlc_source(self):
        hlca = HLCA()
        assert SMA(period=10, source=hlca).name == "SMA_10_HLCA"


class TestMinimumCandles:
    def test_primitive_period(self):
        assert EMA(period=10).minimum_candles == 10

    def test_period_plus_one_indicators(self):
        assert RSI(period=14).minimum_candles == 15

    def test_composite_macd(self):
        assert (
            MACD(fast_period=12, slow_period=26, signal_period=9).minimum_candles == 34
        )

    def test_fake_indicator_period(self):
        assert FakeIndicator(period=10).minimum_candles == 10

    def test_reading_on_expected_candle(self):
        base = datetime(2024, 1, 1, 9, 0)
        candles = [
            Candle(
                open=10 + i,
                high=11 + i,
                low=9 + i,
                close=10 + i,
                volume=100,
                timestamp=base + timedelta(minutes=i),
            )
            for i in range(15)
        ]
        ema = EMA(candles=candles, period=5)
        ema.calculate()

        assert ema.minimum_candles == 5
        assert ema.is_ready is True
        assert ema.series()[4] is not None
        assert ema.series()[:4] == [None, None, None, None]

    def test_is_ready_insufficient_history(self):
        base = datetime(2024, 1, 1, 9, 0)
        candles = [
            Candle(
                open=10 + i,
                high=11 + i,
                low=9 + i,
                close=10 + i,
                volume=100,
                timestamp=base + timedelta(minutes=i),
            )
            for i in range(9)
        ]
        ema = EMA(candles=candles, period=10)

        assert ema.is_ready is False

