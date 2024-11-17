from datetime import datetime

import pytest
from hexital import Candle


@pytest.fixture(name="minimal_conv_candles_exp")
def fixture_minimal_candles():
    candles = [
        Candle(
            open=17313,
            high=2495,
            low=7913,
            close=3715,
            volume=19661,
            timestamp=datetime(2023, 6, 1, 9, 0, 10),
        ),
        Candle(
            open=1401,
            high=3107,
            low=11726,
            close=19148,
            volume=28909,
            timestamp=datetime(2023, 6, 1, 9, 1, 0),
        ),
        Candle(
            open=12715,
            high=1023,
            low=7418,
            close=1451,
            volume=33765,
            timestamp=datetime(2023, 6, 1, 9, 2, 0),
        ),
        Candle(
            open=1743,
            high=16329,
            low=17821,
            close=312,
            volume=3281,
            timestamp=datetime(2023, 6, 1, 9, 3, 0),
        ),
        Candle(
            open=524,
            high=10714,
            low=17233,
            close=7408,
            volume=41793,
            timestamp=datetime(2023, 6, 1, 9, 4, 0),
        ),
        Candle(
            open=4423,
            high=5958,
            low=8885,
            close=8518,
            volume=34913,
            timestamp=datetime(2023, 6, 1, 9, 5, 0),
        ),
        Candle(
            open=13938,
            high=13633,
            low=4930,
            close=17865,
            volume=586,
            timestamp=datetime(2023, 6, 1, 9, 6, 0),
        ),
        Candle(
            open=14473,
            high=18126,
            low=7944,
            close=18898,
            volume=25993,
            timestamp=datetime(2023, 6, 1, 9, 7, 0),
        ),
        Candle(
            open=12482,
            high=19975,
            low=2953,
            close=1531,
            volume=10055,
            timestamp=datetime(2023, 6, 1, 9, 8, 0),
        ),
        Candle(
            open=19302,
            high=6684,
            low=6449,
            close=8399,
            volume=13199,
            timestamp=datetime(2023, 6, 1, 9, 9, 0),
        ),
        Candle(
            open=19823,
            high=4937,
            low=11731,
            close=6331,
            volume=38993,
            timestamp=datetime(2023, 6, 1, 9, 10, 0),
        ),
        Candle(
            open=13664,
            high=12490,
            low=690,
            close=13516,
            volume=30262,
            timestamp=datetime(2023, 6, 1, 9, 11, 0),
        ),
        Candle(
            open=16419,
            high=5992,
            low=16765,
            close=5876,
            volume=47713,
            timestamp=datetime(2023, 6, 1, 9, 12, 0),
        ),
        Candle(
            open=4809,
            high=8290,
            low=10153,
            close=5162,
            volume=14711,
            timestamp=datetime(2023, 6, 1, 9, 13, 0),
        ),
        Candle(
            open=15903,
            high=5267,
            low=17980,
            close=9016,
            volume=36686,
            timestamp=datetime(2023, 6, 1, 9, 14, 0),
        ),
        Candle(
            open=16525,
            high=1498,
            low=18465,
            close=19737,
            volume=41744,
            timestamp=datetime(2023, 6, 1, 9, 15, 0),
        ),
        Candle(
            open=19635,
            high=3724,
            low=13072,
            close=12962,
            volume=47128,
            timestamp=datetime(2023, 6, 1, 9, 16, 0),
        ),
        Candle(
            open=5937,
            high=11655,
            low=16529,
            close=18601,
            volume=9,
            timestamp=datetime(2023, 6, 1, 9, 17, 0),
        ),
        Candle(
            open=16446,
            high=4409,
            low=2003,
            close=6355,
            volume=31307,
            timestamp=datetime(2023, 6, 1, 9, 18, 0),
        ),
        Candle(
            open=2524,
            high=10867,
            low=13215,
            close=13749,
            volume=15750,
            timestamp=datetime(2023, 6, 1, 9, 19, 0),
        ),
    ]

    return candles


@pytest.fixture(name="minimal_conv_candles_t5_expected")
def fixture_minimal_candles_5_minute_expected():
    candles = [
        Candle(
            open=17313,
            high=16329,
            low=7418,
            close=8518,
            volume=162322,
            timestamp=datetime(2023, 6, 1, 9, 5, 0),
        ),
        Candle(
            open=13938,
            high=19975,
            low=2953,
            close=6331,
            volume=88826,
            timestamp=datetime(2023, 6, 1, 9, 10, 0),
        ),
        Candle(
            open=13664,
            high=12490,
            low=690,
            close=19737,
            volume=171116,
            timestamp=datetime(2023, 6, 1, 9, 15, 0),
        ),
        Candle(
            open=19635,
            high=11655,
            low=2003,
            close=13749,
            volume=94194,
            timestamp=datetime(2023, 6, 1, 9, 20, 0),
        ),
    ]
    return candles


@pytest.fixture(name="minimal_conv_candles_t10_expected")
def fixture_minimal_candles_10_minute_expected():
    candles = [
        Candle(
            open=17313,
            high=19975,
            low=2953,
            close=6331,
            volume=251148,
            timestamp=datetime(2023, 6, 1, 9, 10, 0),
        ),
        #
        Candle(
            open=13664,
            high=12490,
            low=690,
            close=13749,
            volume=265310,
            timestamp=datetime(2023, 6, 1, 9, 20, 0),
        ),
    ]
    return candles
