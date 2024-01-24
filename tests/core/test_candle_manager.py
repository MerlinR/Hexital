import copy
from datetime import datetime, timedelta
from typing import List

import pytest
from hexital.core.candle import Candle
from hexital.core.candle_manager import CandleManager


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
            }
        )

        assert manager.candles == [Candle(17213, 2395, 7813, 3615, 19661)]

    def test_append_dict_list(self):
        manager = CandleManager()
        manager.append(
            [
                {"open": 17213, "high": 2395, "low": 7813, "close": 3615, "volume": 19661},
                {"open": 1301, "high": 3007, "low": 11626, "close": 19048, "volume": 28909},
            ]
        )

        assert manager.candles == [
            Candle(17213, 2395, 7813, 3615, 19661),
            Candle(1301, 3007, 11626, 19048, 28909),
        ]

    def test_append_list(self):
        manager = CandleManager()
        manager.append([17213, 2395, 7813, 3615, 19661])

        assert manager.candles == [Candle(17213, 2395, 7813, 3615, 19661)]

    def test_append_list_list(self):
        manager = CandleManager()
        manager.append([[17213, 2395, 7813, 3615, 19661], [1301, 3007, 11626, 19048, 28909]])

        assert manager.candles == [
            Candle(17213, 2395, 7813, 3615, 19661),
            Candle(1301, 3007, 11626, 19048, 28909),
        ]

    def test_append_invalid(self):
        manager = CandleManager()
        with pytest.raises(TypeError):
            manager.append(["Fuck", 2, 3])


class TestMergingCandlesTimeFrame:
    def test_collapse_candles_timeframe_empty(self):
        manager = CandleManager([], "T10", None, "T10")
        assert manager.candles == []

    @pytest.mark.usefixtures("candles", "candles_T5")
    def test_collapse_candles_first(self, candles: List[Candle], candles_T5: List[Candle]):
        manager = CandleManager(candles, "T5", None, "T5")

        assert manager.candles[0] == candles_T5[0]

    @pytest.mark.usefixtures("candles", "candles_T5")
    def test_collapse_candles_second(self, candles: List[Candle], candles_T5: List[Candle]):
        manager = CandleManager(candles, "T5", None, "T5")
        assert manager.candles[1] == candles_T5[1]

    @pytest.mark.usefixtures("candles", "candles_T5")
    def test_collapse_candles_last(self, candles: List[Candle], candles_T5: List[Candle]):
        manager = CandleManager(candles, "T5", None, "T5")
        assert manager.candles[-1] == candles_T5[-1]

    @pytest.mark.usefixtures("candles", "candles_T5")
    def test_collapse_candles_t5(self, candles: List[Candle], candles_T5: List[Candle]):
        manager = CandleManager(candles, "T5", None, "T5")
        assert manager.candles == candles_T5

    @pytest.mark.usefixtures("candles", "candles_T10")
    def test_collapse_candles_t10(self, candles: List[Candle], candles_T10: List[Candle]):
        manager = CandleManager(candles, "T10", None, "T10")
        assert manager.candles == candles_T10

    @pytest.mark.usefixtures("candles", "candles_T5")
    def test_collapse_candles_t5_appended_mini(
        self, candles: List[Candle], candles_T5: List[Candle]
    ):
        data_input = []
        data_input.append(copy.deepcopy(candles_T5[0]))
        data_input.append(copy.deepcopy(candles_T5[1]))
        data_input.append(copy.deepcopy(candles[10]))

        expected = copy.deepcopy(data_input)
        expected[-1].timestamp = datetime(2023, 10, 3, 9, 15)

        manager = CandleManager([data_input[0]], "T5", None, "T5")

        for candle in data_input[1:]:
            manager.append(candle)

        assert manager.candles == expected

    @pytest.mark.usefixtures("candles", "candles_T5")
    def test_collapse_candles_t5_appended_gap_mini(
        self, candles: List[Candle], candles_T5: List[Candle]
    ):
        data_input = []
        data_input.append(copy.deepcopy(candles_T5[0]))
        data_input.append(copy.deepcopy(candles_T5[1]))
        data_input.append(copy.deepcopy(candles_T5[2]))

        expected = copy.deepcopy(data_input)
        expected.append(copy.deepcopy(candles[20]))
        expected[-1].timestamp = datetime(2023, 10, 3, 9, 25)

        manager = CandleManager(data_input, "T5", None, "T5")
        manager.append(copy.deepcopy(candles[20]))

        assert manager.candles == expected

    @pytest.mark.usefixtures("candles", "candles_T5")
    def test_collapse_candles_t5_appended(self, candles: List[Candle], candles_T5: List[Candle]):
        manager = CandleManager([candles[0]], "T5", None, "T5")
        for candle in candles[1:]:
            manager.append(candle)

        assert manager.candles == candles_T5

    @pytest.mark.usefixtures("candles", "candles_T10")
    def test_collapse_candles_t10_appended(self, candles: List[Candle], candles_T10: List[Candle]):
        manager = CandleManager([candles[0]], "T10", None, "T10")
        for candle in candles[1:]:
            manager.append(candle)

        assert manager.candles == candles_T10

    @pytest.mark.usefixtures("candles", "candles_T5")
    def test_collapse_candles_t5_multiple_collapse(
        self, candles: List[Candle], candles_T5: List[Candle]
    ):
        manager = CandleManager(candles, "T5", None, "T5")
        assert manager.candles == candles_T5

        manager.collapse_candles()
        assert manager.candles == candles_T5

        manager.collapse_candles()
        assert manager.candles == candles_T5

    @pytest.mark.usefixtures("candles", "candles_T5")
    def test_collapse_candles_t5_mixed_neat(self, candles: List[Candle], candles_T5: List[Candle]):
        manager = CandleManager(candles[:10], "T5", None, "T5")
        assert manager.candles == candles_T5[:2]

        manager.append(candles[10:])
        assert manager.candles == candles_T5

    @pytest.mark.usefixtures("candles", "candles_T5")
    def test_collapse_candles_t5_mixed_messy(
        self, candles: List[Candle], candles_T5: List[Candle]
    ):
        manager = CandleManager(candles[:7], "T5", None, "T5")
        manager.append(candles[7:])
        assert manager.candles == candles_T5

    @pytest.mark.usefixtures("candles", "candles_T5")
    def test_collapse_candles_t5_missing_section(
        self, candles: List[Candle], candles_T5: List[Candle]
    ):
        cut_candles = candles[:5] + candles[-2:]
        manager = CandleManager(cut_candles, "T5", None, "T5")
        assert manager.candles == [candles_T5[0], candles_T5[-1]]

    @pytest.mark.usefixtures("candles", "candles_T5")
    def test_collapse_candles_t5_missing_section_two(
        self, candles: List[Candle], candles_T5: List[Candle]
    ):
        cut_candles = candles[:5] + candles[10:15]
        manager = CandleManager(cut_candles, "T5", None, "T5")
        assert manager.candles == [candles_T5[0], candles_T5[2]]

    @pytest.mark.usefixtures("candles", "candles_T5")
    def test_collapse_candles_t5_missing_section_three(
        self, candles: List[Candle], candles_T5: List[Candle]
    ):
        data_input = []
        data_input.append(copy.deepcopy(candles_T5[0]))
        data_input.append(copy.deepcopy(candles_T5[1]))
        data_input.append(copy.deepcopy(candles_T5[2]))
        data_input.append(copy.deepcopy(candles[20]))

        expected = copy.deepcopy(data_input)
        expected[-1].timestamp = datetime(2023, 10, 3, 9, 25)

        manager = CandleManager(data_input, "T5", None, "T5")

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

        manager = CandleManager(data_input, "T5", None, "T5")
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
        manager = CandleManager([], "T5", None, "T5")

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

    manager = CandleManager(cut_candles, "T5", None, "T5", True)
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

    manager = CandleManager(cut_candles, "T5", None, "T5", True)

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

    manager = CandleManager(cut_candles, "T5", None, "T5", True)

    assert manager.candles == [candles_T5[0]] + filler_candles + [candles_T5[-1]]
