import copy
from datetime import datetime, timedelta
from typing import List

import pytest
from hexital import Candle
from hexital.core.candle_manager import CandleManager
from test_candlestick import FakeType


class TestCandleAppending:
    @pytest.mark.usefixtures("minimal_candles")
    def test_append_candle(self, minimal_candles):
        new_candle = minimal_candles.pop()
        manager = CandleManager()
        manager.append(new_candle)

        assert manager.candles == [new_candle]

    def test_append_list_nada(self):
        manager = CandleManager()
        manager.append([])

        assert manager.candles == []

    @pytest.mark.usefixtures("minimal_candles")
    def test_append_candle_list(self, minimal_candles):
        manager = CandleManager()
        manager.append(minimal_candles)

        assert manager.candles == minimal_candles

    def test_append_dict(self):
        manager = CandleManager()
        manager.append(
            {
                "open": 17213,
                "high": 2395,
                "low": 7813,
                "close": 3615,
                "volume": 19661,
                "timestamp": datetime(2023, 10, 3, 9, 0),
            }
        )

        assert manager.candles == [
            Candle(
                17213,
                2395,
                7813,
                3615,
                19661,
                timestamp=datetime(2023, 10, 3, 9, 0),
            )
        ]

    def test_append_dict_list(self):
        manager = CandleManager()
        manager.append(
            [
                {
                    "open": 17213,
                    "high": 2395,
                    "low": 7813,
                    "close": 3615,
                    "volume": 19661,
                    "timestamp": datetime(2023, 10, 3, 9, 0),
                },
                {
                    "open": 1301,
                    "high": 3007,
                    "low": 11626,
                    "close": 19048,
                    "volume": 28909,
                    "timestamp": datetime(2023, 10, 3, 9, 5),
                },
            ]
        )

        assert manager.candles == [
            Candle(
                17213,
                2395,
                7813,
                3615,
                19661,
                timestamp=datetime(2023, 10, 3, 9, 0),
            ),
            Candle(
                1301,
                3007,
                11626,
                19048,
                28909,
                timestamp=datetime(2023, 10, 3, 9, 5),
            ),
        ]

    def test_append_list(self):
        manager = CandleManager()
        manager.append([datetime(2023, 10, 3, 9, 0), 17213, 2395, 7813, 3615, 19661])

        assert manager.candles == [
            Candle(17213, 2395, 7813, 3615, 19661, timestamp=datetime(2023, 10, 3, 9, 0))
        ]

    def test_append_list_list(self):
        manager = CandleManager()
        manager.append(
            [
                [datetime(2023, 10, 3, 9, 0), 17213, 2395, 7813, 3615, 19661],
                [datetime(2023, 10, 3, 9, 5), 1301, 3007, 11626, 19048, 28909],
            ]
        )

        assert manager.candles == [
            Candle(17213, 2395, 7813, 3615, 19661, timestamp=datetime(2023, 10, 3, 9, 0)),
            Candle(1301, 3007, 11626, 19048, 28909, timestamp=datetime(2023, 10, 3, 9, 5)),
        ]

    def test_append_invalid(self):
        manager = CandleManager()
        with pytest.raises(IndexError):
            manager.append(["Fuck", 2, 3])


class TestCandleTimeframeAppending:
    def test_default(self):
        manager = CandleManager()
        manager.append(
            [
                Candle(17213, 2395, 7813, 3615, 19661, timestamp=datetime(2023, 10, 3, 9, 5)),
                Candle(14842, 14842, 14831, 14835, 540, timestamp=datetime(2023, 10, 3, 9, 10)),
            ]
        )
        assert manager.candles == [
            Candle(17213, 2395, 7813, 3615, 19661, timestamp=datetime(2023, 10, 3, 9, 5)),
            Candle(14842, 14842, 14831, 14835, 540, timestamp=datetime(2023, 10, 3, 9, 10)),
        ]

    def test_default_timeframe(self):
        manager = CandleManager(timeframe=timedelta(minutes=5))
        manager.append(
            [
                Candle(17213, 2395, 7813, 3615, 19661, timestamp=datetime(2023, 10, 3, 9, 5)),
                Candle(14842, 14842, 14831, 14835, 540, timestamp=datetime(2023, 10, 3, 9, 10)),
            ]
        )
        assert manager.candles == [
            Candle(
                17213,
                2395,
                7813,
                3615,
                19661,
                timestamp=datetime(2023, 10, 3, 9, 5),
                timeframe=timedelta(minutes=5),
            ),
            Candle(14842, 14842, 14831, 14835, 540, timestamp=datetime(2023, 10, 3, 9, 10)),
        ]

    def test_candle_timeframe_append(self):
        manager = CandleManager(
            [Candle(17213, 2395, 7813, 3615, 19661, timestamp=datetime(2023, 10, 3, 9, 5))],
        )
        manager.append(
            Candle(14842, 14842, 14831, 14835, 540, timestamp=datetime(2023, 10, 3, 9, 10)),
        )
        assert manager.candles == [
            Candle(17213, 2395, 7813, 3615, 19661, timestamp=datetime(2023, 10, 3, 9, 5)),
            Candle(14842, 14842, 14831, 14835, 540, timestamp=datetime(2023, 10, 3, 9, 10)),
        ]

    def test_candle_timeframe_append_same(self):
        manager = CandleManager(
            [Candle(17213, 2395, 7813, 3615, 19661, timestamp=datetime(2023, 10, 3, 9, 5))],
            timeframe=timedelta(minutes=5),
        )
        manager.append(
            Candle(
                14842,
                14842,
                14831,
                14835,
                540,
                timestamp=datetime(2023, 10, 3, 9, 10),
                timeframe=timedelta(minutes=5),
            ),
        )
        assert manager.candles == [
            Candle(17213, 2395, 7813, 3615, 19661, timestamp=datetime(2023, 10, 3, 9, 5)),
            Candle(14842, 14842, 14831, 14835, 540, timestamp=datetime(2023, 10, 3, 9, 10)),
        ]

    def test_candle_timeframe_append_lower(self):
        manager = CandleManager(
            [Candle(17213, 2395, 7813, 3615, 19661, timestamp=datetime(2023, 10, 3, 9, 5))],
            timeframe=timedelta(minutes=5),
        )
        manager.append(
            Candle(
                14842,
                14842,
                14831,
                14835,
                540,
                timestamp=datetime(2023, 10, 3, 9, 6),
                timeframe=timedelta(minutes=1),
            ),
        )
        assert manager.candles == [
            Candle(
                17213,
                2395,
                7813,
                3615,
                19661,
                timestamp=datetime(2023, 10, 3, 9, 5),
                timeframe=timedelta(minutes=5),
            ),
            Candle(
                14842,
                14842,
                14831,
                14835,
                540,
                timestamp=datetime(2023, 10, 3, 9, 10),
            ),
        ]

    def test_candle_timeframe_append_lower_two(self):
        manager = CandleManager(
            [Candle(17213, 2395, 7813, 3615, 19661, timestamp=datetime(2023, 10, 3, 9, 5))],
            timeframe=timedelta(minutes=5),
        )
        manager.append(
            Candle(
                14842,
                14842,
                14831,
                15000,
                540,
                timestamp=datetime(2023, 10, 3, 9, 6),
                timeframe=timedelta(minutes=1),
            ),
        )
        manager.append(
            Candle(
                15000,
                16000,
                14831,
                16000,
                540,
                timestamp=datetime(2023, 10, 3, 9, 7),
                timeframe=timedelta(minutes=1),
            ),
        )
        manager.collapse_candles()
        assert manager.candles == [
            Candle(17213, 2395, 7813, 3615, 19661, timestamp=datetime(2023, 10, 3, 9, 5)),
            Candle(14842, 16000, 14831, 16000, 1080, timestamp=datetime(2023, 10, 3, 9, 10)),
        ]

    def test_candle_timeframe_append_higher(self):
        manager = CandleManager(
            [Candle(17213, 2395, 7813, 3615, 19661, timestamp=datetime(2023, 10, 3, 9, 5))],
            timeframe=timedelta(minutes=5),
        )
        manager.append(
            Candle(
                14842,
                14842,
                14831,
                14835,
                540,
                timestamp=datetime(2023, 10, 3, 9, 15),
                timeframe=timedelta(minutes=10),
            ),
        )
        assert manager.candles == [
            Candle(17213, 2395, 7813, 3615, 19661, timestamp=datetime(2023, 10, 3, 9, 5)),
        ]


class TestCandleSort:
    def test_sort_candles(self):
        manager = CandleManager()
        manager.candles = [
            Candle(17213, 2395, 7813, 3615, 19661, timestamp=datetime(2023, 10, 3, 9, 5)),
            Candle(14842, 14842, 14831, 14835, 540, timestamp=datetime(2023, 10, 3, 9, 10)),
            Candle(1301, 3007, 11626, 19048, 28909, timestamp=datetime(2023, 10, 3, 9, 0)),
        ]

        manager.sort_candles()

        assert manager.candles == [
            Candle(1301, 3007, 11626, 19048, 28909, timestamp=datetime(2023, 10, 3, 9, 0)),
            Candle(17213, 2395, 7813, 3615, 19661, timestamp=datetime(2023, 10, 3, 9, 5)),
            Candle(14842, 14842, 14831, 14835, 540, timestamp=datetime(2023, 10, 3, 9, 10)),
        ]

    def test_sort_candles_timeframed(self):
        manager = CandleManager(
            timeframe=timedelta(minutes=5),
        )
        manager.candles = [
            Candle(1301, 3007, 11626, 19048, 28909, timestamp=datetime(2023, 10, 3, 9, 0)),
            Candle(17213, 2395, 7813, 3615, 19661, timestamp=datetime(2023, 10, 3, 9, 5)),
            Candle(14842, 14842, 14831, 14835, 540, timestamp=datetime(2023, 10, 3, 9, 10)),
        ]

        manager.candles.append(
            Candle(1301, 3007, 11626, 19048, 28909, timestamp=datetime(2023, 10, 3, 9, 2))
        )
        manager.sort_candles()

        assert manager.candles == [
            Candle(1301, 3007, 11626, 19048, 28909, timestamp=datetime(2023, 10, 3, 9, 0)),
            Candle(17213, 2395, 7813, 3615, 19661, timestamp=datetime(2023, 10, 3, 9, 5)),
            Candle(1301, 3007, 11626, 19048, 28909, timestamp=datetime(2023, 10, 3, 9, 2)),
            Candle(14842, 14842, 14831, 14835, 540, timestamp=datetime(2023, 10, 3, 9, 10)),
        ]

    def test_sort_candles_append(self):
        manager = CandleManager()
        manager.append(
            [
                Candle(17213, 2395, 7813, 3615, 19661, timestamp=datetime(2023, 10, 3, 9, 5)),
                Candle(14842, 14842, 14831, 14835, 540, timestamp=datetime(2023, 10, 3, 9, 10)),
                Candle(1301, 3007, 11626, 19048, 28909, timestamp=datetime(2023, 10, 3, 9, 0)),
            ]
        )
        assert manager.candles == [
            Candle(1301, 3007, 11626, 19048, 28909, timestamp=datetime(2023, 10, 3, 9, 0)),
            Candle(17213, 2395, 7813, 3615, 19661, timestamp=datetime(2023, 10, 3, 9, 5)),
            Candle(14842, 14842, 14831, 14835, 540, timestamp=datetime(2023, 10, 3, 9, 10)),
        ]

    def test_sort_candles_append_timeframed(self):
        manager = CandleManager(
            [
                Candle(1301, 3007, 11626, 19048, 28909, timestamp=datetime(2023, 10, 3, 9, 0)),
                Candle(17213, 2395, 7813, 3615, 19661, timestamp=datetime(2023, 10, 3, 9, 5)),
                Candle(14842, 14842, 14831, 14835, 540, timestamp=datetime(2023, 10, 3, 9, 10)),
            ],
            timeframe=timedelta(minutes=5),
        )

        manager.append(
            Candle(1301, 3007, 11626, 19048, 28909, timestamp=datetime(2023, 10, 3, 9, 2))
        )

        assert manager.candles == [
            Candle(1301, 3007, 11626, 19048, 28909, timestamp=datetime(2023, 10, 3, 9, 0)),
            Candle(1301, 3007, 7813, 3615, 48570, timestamp=datetime(2023, 10, 3, 9, 5)),
            Candle(14842, 14842, 14831, 14835, 540, timestamp=datetime(2023, 10, 3, 9, 10)),
        ]

    def test_sort_candles_append_timeframed_on_untimeframed(self):
        manager = CandleManager([])

        manager.append(
            Candle(
                1301,
                3007,
                7813,
                3615,
                48570,
                timestamp=datetime(2023, 10, 3, 9, 5),
                timeframe=timedelta(minutes=5),
            )
        )

        assert manager.candles == [
            Candle(1301, 3007, 7813, 3615, 48570, timestamp=datetime(2023, 10, 3, 9, 5)),
        ]


class TestMergingCandlesTimeFrame:
    def test_collapse_candles_timeframe_empty(self):
        manager = CandleManager([], timeframe=timedelta(minutes=10))
        assert manager.candles == []

    @pytest.mark.usefixtures("candles", "candles_T5")
    def test_collapse_candles_first(self, candles: List[Candle], candles_T5: List[Candle]):
        manager = CandleManager(candles, timeframe=timedelta(minutes=5))

        assert manager.candles[0] == candles_T5[0]

    @pytest.mark.usefixtures("candles", "candles_T5")
    def test_collapse_candles_second(self, candles: List[Candle], candles_T5: List[Candle]):
        manager = CandleManager(candles, timeframe=timedelta(minutes=5))
        assert manager.candles[1] == candles_T5[1]

    @pytest.mark.usefixtures("candles", "candles_T5")
    def test_collapse_candles_last(self, candles: List[Candle], candles_T5: List[Candle]):
        manager = CandleManager(candles, timeframe=timedelta(minutes=5))
        assert manager.candles[-1] == candles_T5[-1]

    @pytest.mark.usefixtures("candles", "candles_T5")
    def test_collapse_candles_t5(self, candles: List[Candle], candles_T5: List[Candle]):
        manager = CandleManager(candles, timeframe=timedelta(minutes=5))
        assert manager.candles == candles_T5

    @pytest.mark.usefixtures("candles", "candles_T10")
    def test_collapse_candles_t10(self, candles: List[Candle], candles_T10: List[Candle]):
        manager = CandleManager(candles, timeframe=timedelta(minutes=10))
        assert manager.candles == candles_T10

    @pytest.mark.usefixtures("candles", "candles_T5")
    def test_collapse_candles_t5_appended_mini(
        self, candles: List[Candle], candles_T5: List[Candle]
    ):
        data_input = []
        data_input.append(candles_T5[0])
        data_input.append(candles_T5[1])
        data_input.append(candles[10])

        expected = data_input
        expected[-1].timestamp = datetime(2023, 10, 3, 9, 15)

        manager = CandleManager([data_input[0]], timeframe=timedelta(minutes=5))

        for candle in data_input[1:]:
            manager.append(candle)

        assert manager.candles == expected

    @pytest.mark.usefixtures("candles", "candles_T5")
    def test_collapse_candles_t5_appended_gap_mini(
        self, candles: List[Candle], candles_T5: List[Candle]
    ):
        data_input = []
        data_input.append(candles_T5[0])
        data_input.append(candles_T5[1])
        data_input.append(candles_T5[2])

        expected = data_input
        expected.append(candles[20])
        expected[-1].timestamp = datetime(2023, 10, 3, 9, 25)

        manager = CandleManager(data_input, timeframe=timedelta(minutes=5))
        manager.append(candles[20])

        assert manager.candles == expected

    @pytest.mark.usefixtures("candles", "candles_T5")
    def test_collapse_candles_t5_appended(self, candles: List[Candle], candles_T5: List[Candle]):
        manager = CandleManager([candles[0]], timeframe=timedelta(minutes=5))
        for candle in candles[1:]:
            manager.append(candle)

        assert manager.candles == candles_T5

    @pytest.mark.usefixtures("candles", "candles_T10")
    def test_collapse_candles_t10_appended(self, candles: List[Candle], candles_T10: List[Candle]):
        manager = CandleManager([candles[0]], timeframe=timedelta(minutes=10))
        for candle in candles[1:]:
            manager.append(candle)

        assert manager.candles == candles_T10

    @pytest.mark.usefixtures("candles", "candles_T5")
    def test_collapse_candles_t5_multiple_collapse(
        self, candles: List[Candle], candles_T5: List[Candle]
    ):
        manager = CandleManager(candles, timeframe=timedelta(minutes=5))
        assert manager.candles == candles_T5

        manager.collapse_candles()
        assert manager.candles == candles_T5

        manager.collapse_candles()
        assert manager.candles == candles_T5

    @pytest.mark.usefixtures("candles", "candles_T5")
    def test_collapse_candles_t5_mixed_neat(self, candles: List[Candle], candles_T5: List[Candle]):
        manager = CandleManager(candles[:10], timeframe=timedelta(minutes=5))
        assert manager.candles == candles_T5[:2]

        manager.append(candles[10:])
        assert manager.candles == candles_T5

    @pytest.mark.usefixtures("candles", "candles_T5")
    def test_collapse_candles_t5_mixed_messy(
        self, candles: List[Candle], candles_T5: List[Candle]
    ):
        manager = CandleManager(candles[:7], timeframe=timedelta(minutes=5))
        manager.append(candles[7:])
        assert manager.candles == candles_T5

    @pytest.mark.usefixtures("candles", "candles_T5")
    def test_collapse_candles_t5_missing_section(
        self, candles: List[Candle], candles_T5: List[Candle]
    ):
        cut_candles = candles[:5] + candles[-2:]
        manager = CandleManager(cut_candles, timeframe=timedelta(minutes=5))
        assert manager.candles == [candles_T5[0], candles_T5[-1]]

    @pytest.mark.usefixtures("candles", "candles_T5")
    def test_collapse_candles_t5_missing_section_two(
        self, candles: List[Candle], candles_T5: List[Candle]
    ):
        cut_candles = candles[:5] + candles[10:15]
        manager = CandleManager(cut_candles, timeframe=timedelta(minutes=5))
        assert manager.candles == [candles_T5[0], candles_T5[2]]

    @pytest.mark.usefixtures("candles", "candles_T5")
    def test_collapse_candles_t5_missing_section_three(
        self, candles: List[Candle], candles_T5: List[Candle]
    ):
        data_input = []
        data_input.append(candles_T5[0])
        data_input.append(candles_T5[1])
        data_input.append(candles_T5[2])
        data_input.append(candles[20])

        expected = data_input
        expected[-1].timestamp = datetime(2023, 10, 3, 9, 25)

        manager = CandleManager(data_input, timeframe=timedelta(minutes=5))

        assert manager.candles == expected

    @pytest.mark.usefixtures("candles", "candles_T5")
    def test_collapse_candles_t5_missing_section_messy(self):
        data_input = [
            Candle(33419.3, 33419.3, 33410.8, 33410.8, 24, timestamp=datetime(2023, 10, 3, 1, 47)),
            Candle(33411.3, 33413.8, 33406.8, 33406.8, 16, timestamp=datetime(2023, 10, 3, 1, 47)),
            Candle(33399.3, 33401.3, 33397.8, 33399.8, 9, timestamp=datetime(2023, 10, 3, 2, 59)),
            Candle(33399.3, 33399.8, 33396.8, 33397.3, 5, timestamp=datetime(2023, 10, 3, 3, 00)),
        ]
        expected = [
            Candle(
                open=33419.3,
                high=33419.3,
                low=33406.8,
                close=33406.8,
                volume=40,
                timestamp=datetime(2023, 10, 3, 1, 50),
            ),
            Candle(
                open=33399.3,
                high=33401.3,
                low=33396.8,
                close=33397.3,
                volume=14,
                timestamp=datetime(2023, 10, 3, 3, 00),
            ),
        ]

        manager = CandleManager(data_input, timeframe=timedelta(minutes=5))
        assert manager.candles == expected

    @pytest.mark.usefixtures("candles", "candles_T5")
    def test_collapse_candles_t5_missing_section_messy_append(self):
        data_input = [
            Candle(33419.3, 33419.3, 33410.8, 33410.8, 24, timestamp=datetime(2023, 10, 3, 1, 47)),
            Candle(33411.3, 33413.8, 33406.8, 33406.8, 16, timestamp=datetime(2023, 10, 3, 1, 47)),
            Candle(33399.3, 33401.3, 33397.8, 33399.8, 9, timestamp=datetime(2023, 10, 3, 2, 59)),
            Candle(33399.3, 33399.8, 33396.8, 33397.3, 5, timestamp=datetime(2023, 10, 3, 3, 00)),
        ]
        expected = [
            Candle(
                open=33419.3,
                high=33419.3,
                low=33406.8,
                close=33406.8,
                volume=40,
                timestamp=datetime(2023, 10, 3, 1, 50),
            ),
            Candle(
                open=33399.3,
                high=33401.3,
                low=33396.8,
                close=33397.3,
                volume=14,
                timestamp=datetime(2023, 10, 3, 3, 00),
            ),
        ]
        manager = CandleManager([], timeframe=timedelta(minutes=5))

        for candle in data_input:
            manager.append(candle)

        assert manager.candles == expected


@pytest.mark.usefixtures("candles", "candles_T5")
def test_collapse_candles_t5_missing_section_fill(candles_T5: List[Candle]):
    cut_candles = [candles_T5[0]] + [candles_T5[2]]

    filler = Candle(
        candles_T5[0].close,
        candles_T5[0].close,
        candles_T5[0].close,
        candles_T5[0].close,
        0,
        timestamp=candles_T5[0].timestamp + timedelta(minutes=5),
    )

    manager = CandleManager(cut_candles, timeframe=timedelta(minutes=5), timeframe_fill=True)
    assert manager.candles == [
        candles_T5[0],
        filler,
        candles_T5[2],
    ]


@pytest.mark.usefixtures("candles", "candles_T5")
def test_collapse_candles_t5_missing_section_fill_all(candles_T5: List[Candle]):
    cut_candles = [candles_T5[0]] + [candles_T5[-1]]

    filler_candles = []
    for i in range(len(candles_T5) - 2):
        filler_candles.append(
            Candle(
                candles_T5[0].close,
                candles_T5[0].close,
                candles_T5[0].close,
                candles_T5[0].close,
                0,
                timestamp=candles_T5[0].timestamp + (timedelta(minutes=5) * (i + 1)),
            )
        )

    manager = CandleManager(cut_candles, timeframe=timedelta(minutes=5), timeframe_fill=True)

    assert manager.candles == [candles_T5[0]] + filler_candles + [candles_T5[-1]]


@pytest.mark.usefixtures("candles", "candles_T5")
def test_collapse_candles_t5_missing_section_fill_all_extra(
    candles: List[Candle], candles_T5: List[Candle]
):
    cut_candles = candles[:5] + candles[-2:]

    blank_candle = copy.deepcopy(candles_T5[0])
    blank_candle.open = blank_candle.close
    blank_candle.high = blank_candle.close
    blank_candle.low = blank_candle.close
    blank_candle.volume = 0

    filler_candles = []
    for i in range(99):
        blank_candle.timestamp += timedelta(minutes=5)
        filler_candles.append(copy.deepcopy(blank_candle))

    manager = CandleManager(cut_candles, timeframe=timedelta(minutes=5), timeframe_fill=True)

    assert manager.candles == [candles_T5[0]] + filler_candles + [candles_T5[-1]]


class TestCandleConversion:
    @pytest.mark.usefixtures("candles", "minimal_conv_candles_t5_expected")
    def test_conversion_manager_timeframe(
        self, minimal_candles: List[Candle], minimal_conv_candles_t5_expected: List[Candle]
    ):
        manager = CandleManager(
            minimal_candles, timeframe=timedelta(minutes=5), candlestick_type=FakeType()
        )
        manager._tasks()

        assert manager.candles == minimal_conv_candles_t5_expected

    @pytest.mark.usefixtures("candles", "minimal_conv_candles_t5_expected")
    def test_conversion_manager_timeframe_multi_convert(
        self, minimal_candles: List[Candle], minimal_conv_candles_t5_expected: List[Candle]
    ):
        manager = CandleManager(
            minimal_candles, timeframe=timedelta(minutes=5), candlestick_type=FakeType()
        )
        manager.convert_candles()
        manager.convert_candles()
        manager.convert_candles()

        assert manager.candles == minimal_conv_candles_t5_expected

    @pytest.mark.usefixtures("candles", "minimal_conv_candles_t5_expected")
    def test_conversion_manager_timeframe_merge_messy(
        self, minimal_candles: List[Candle], minimal_conv_candles_t5_expected: List[Candle]
    ):
        manager = CandleManager(
            minimal_candles[:3], timeframe=timedelta(minutes=5), candlestick_type=FakeType()
        )

        manager._tasks()
        manager.append(minimal_candles[3:])

        assert manager.candles == minimal_conv_candles_t5_expected
