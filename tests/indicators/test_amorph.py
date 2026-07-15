from hexital import Candle, movement, patterns
from hexital.core.hexital import Hexital
from hexital.indicators import Amorph


def fake_pattern(candles: list[Candle], index=-1):
    return 1


def test_method_amorph(candles):
    test = Amorph(analysis=patterns.doji, candles=candles)
    test.calculate()
    assert test.reading() is not None


def test_amorph_multi_arguments(candles_untimeframed):
    test = Amorph(analysis=patterns.doji, candles=candles_untimeframed, lookback=20)
    test.calculate()
    assert test.name == "doji"


def test_amorph_dict_arguments(candles):
    test = Amorph(analysis=patterns.doji, candles=candles, args={"lookback": 20})
    test.calculate()
    assert test.name == "doji"


def test_amorph_merged_aguments(candles):
    test = Amorph(
        analysis=patterns.doji,
        candles=candles,
        lookback=20,
        name="MERGED_ARGS",
    )
    test.calculate()
    assert test.name == "MERGED_ARGS"


def test_movement_amorph(candles):
    test = Amorph(analysis=movement.positive, candles=candles)
    test.calculate()
    assert test.reading("positive") is not None


def test_movement_amorph_args(candles):
    test = Amorph(analysis=movement.positive, candles=candles, name="boobies")
    test.calculate()
    assert test.reading("boobies") is not None


def test_movement_amorph_kawgs(candles_untimeframed):
    test = Amorph(
        analysis=movement.above,
        candles=candles_untimeframed,
        indicator="open",
        indicator_cmp="low",
    )
    test.calculate()
    assert test.reading("above") is not None


def test_amorph_custom(candles):
    test = Amorph(analysis=fake_pattern, candles=candles)
    test.calculate()
    assert test.reading("fake_pattern") is not None


def test_amorph_settings_roundtrip(candles):
    original = Amorph(analysis=patterns.doji, candles=candles, lookback=20)
    original.calculate()

    strategy = Hexital("x", candles, [original.settings])
    rebuilt = strategy.indicator(original.name)
    rebuilt.candles = candles
    rebuilt.calculate()

    assert rebuilt.name == original.name
    assert rebuilt._analysis_kwargs == original._analysis_kwargs
    assert rebuilt.series() == original.series()


def test_amorph_settings_roundtrip_via_hexital(candles):
    strategy = Hexital("Test Strategy", candles, [Amorph(analysis=patterns.doji, lookback=20)])
    strategy.calculate()

    as_dict = strategy.settings
    as_dict["candles"] = candles
    rebuilt = Hexital(**as_dict)
    rebuilt.calculate()

    assert rebuilt.settings["indicators"] == strategy.settings["indicators"]
    assert rebuilt.series("doji") == strategy.series("doji")


def test_amorph_settings_roundtrip_movement(candles_untimeframed):
    original = Amorph(
        analysis=movement.above,
        candles=candles_untimeframed,
        indicator="open",
        indicator_cmp="low",
    )
    original.calculate()

    strategy = Hexital("x", candles_untimeframed, [original.settings])
    rebuilt = strategy.indicator(original.name)
    rebuilt.candles = candles_untimeframed
    rebuilt.calculate()

    assert rebuilt._analysis_kwargs == original._analysis_kwargs
    assert rebuilt.series() == original.series()
