import common
from hexital import EMA, Candle, Hexital

PATH = "tests/data/"


def main(candles):
    strat = Hexital("test", [], [EMA(), EMA(timeframe="T5")])

    for i, candle in enumerate(candles):
        strat.append(candle)


if __name__ == "__main__":
    candles = Candle.from_dicts(common.load_json_candles("test_candles", PATH))
    with common.Profiler("Hexital"):
        main(candles)
