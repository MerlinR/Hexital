import common
from hexital import Candle, indicators

PATH = "tests/data/"


def main(candles):
    test = indicators.Supertrend()

    for i, candle in enumerate(candles):
        test.append(candle)


if __name__ == "__main__":
    candles = Candle.from_dicts(common.load_json_candles("test_candles", PATH))
    with common.Profiler("Supertrend"):
        main(candles)
