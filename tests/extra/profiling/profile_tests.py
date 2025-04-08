import common
from hexital import Candle, Hexital, indicators

PATH = "tests/data/"


def profile_ema(candles):
    strat = Hexital("test", [], [indicators.EMA(), indicators.EMA(timeframe="T5")])

    for i, candle in enumerate(candles):
        strat.append(candle)


def profile_supertrend(candles):
    test = indicators.Supertrend()

    for i, candle in enumerate(candles):
        test.append(candle)


def default(candles):
    strat = Hexital("test", [], [indicators.EMA(), indicators.EMA()])

    for i, candle in enumerate(candles):
        strat.append(candle)


def default_prepend(candles):
    strat = Hexital("test", [], [indicators.EMA(), indicators.EMA()])

    for i, candle in enumerate(candles):
        strat.prepend(candle)


def timeframe_1t(candles):
    strat = Hexital("test", [], [indicators.EMA(), indicators.EMA(timeframe="T1")])

    for i, candle in enumerate(candles):
        strat.append(candle)


def timeframe_prepend_1t(candles):
    strat = Hexital("test", [], [indicators.EMA(), indicators.EMA(timeframe="T1")])

    for candle in reversed(candles):
        strat.prepend(candle)


def timeframe_5t(candles):
    strat = Hexital("test", [], [indicators.EMA(), indicators.EMA(timeframe="T5")])

    for i, candle in enumerate(candles):
        strat.append(candle)


def timeframe_append(candles):
    strat = Hexital("test", [], [indicators.Supertrend(), indicators.Supertrend(timeframe="T5")])

    for candle in candles:
        strat.append(candle)


def timeframe_prepend(candles):
    strat = Hexital("test", [], [indicators.Supertrend(), indicators.Supertrend(timeframe="T5")])

    for candle in reversed(candles):
        strat.prepend(candle)


if __name__ == "__main__":
    candles = Candle.from_dicts(common.load_json_candles("test_candles", PATH))
    with common.Profiler("EMA_multi_timeframes"):
        profile_ema(candles)

    with common.Profiler("Supertrend"):
        profile_supertrend(candles)

    with common.Profiler("Timeframes_default"):
        default(candles)

    with common.Profiler("Timeframes_default_prepend"):
        default_prepend(candles)

    with common.Profiler("Timeframes_T1"):
        timeframe_1t(candles)

    with common.Profiler("Timeframes_T1_prepend"):
        timeframe_prepend_1t(candles)

    with common.Profiler("Timeframes_T5"):
        timeframe_5t(candles)

    with common.Profiler("Timeframes_supertrend_append"):
        timeframe_append(candles)

    with common.Profiler("Timeframes_supertrend_prepend"):
        timeframe_prepend(candles)
