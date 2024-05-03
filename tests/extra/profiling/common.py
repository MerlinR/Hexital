import cProfile
import json
import os
import pstats
from datetime import datetime

PATH = "./tests/data/"
PROFS = "./prof/"


def load_json_candles(name: str, path: str) -> list:
    csv_file = open(f"{path}{name}.json")
    raw_candles = json.load(csv_file)
    for candle in raw_candles:
        candle["timestamp"] = datetime.strptime(candle["timestamp"], "%Y-%m-%dT%H:%M:%S")
    return raw_candles


class Profiler:
    def __init__(self, name: str):
        self.name = name
        if os.path.exists(PROFS) is False:
            os.mkdir(PROFS)

    def __enter__(self):
        self.profiler = cProfile.Profile()
        self.profiler.enable()
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        self.profiler.disable()
        stats = pstats.Stats(self.profiler).sort_stats("cumtime")
        stats.dump_stats(f"{PROFS}/{self.name}.prof")
