import copy
from datetime import datetime, timedelta
from typing import List

import pytest
from hexital.core import Candle
from hexital.lib.candle_extension import (
    candles_sum,
    collapse_candles_timeframe,
    reading_as_list,
    reading_by_index,
    reading_count,
    fill_missing_candles,
    reading_period,
)


class TestReadByIndex:
    @pytest.mark.usefixtures("minimal_candles")
    def test_basic(self, minimal_candles: List[Candle]):
        assert reading_by_index(minimal_candles, "high") == 10767

    def test_basic_invalid(self):
        assert reading_by_index([], "high") is None

    @pytest.mark.usefixtures("minimal_candles")
    def test_indexed(self, minimal_candles: List[Candle]):
        assert reading_by_index(minimal_candles, "high", index=5) == 5858

    @pytest.mark.usefixtures("minimal_candles")
    def test_indexed_invalid(self, minimal_candles: List[Candle]):
        assert reading_by_index(minimal_candles, "high", index=6000) is None

    @pytest.mark.usefixtures("minimal_candles")
    def test_indicator(self, minimal_candles: List[Candle]):
        assert reading_by_index(minimal_candles, "ATR") == 2000

    @pytest.mark.usefixtures("minimal_candles")
    def test_nested_indicator(self, minimal_candles: List[Candle]):
        assert reading_by_index(minimal_candles, "NATR") == {"nested": 2001}

    @pytest.mark.usefixtures("minimal_candles")
    def test_inner_nested_indicator(self, minimal_candles: List[Candle]):
        assert reading_by_index(minimal_candles, "NATR.nested") == 2001

    @pytest.mark.usefixtures("minimal_candles")
    def test_indicator_indexed(self, minimal_candles: List[Candle]):
        assert reading_by_index(minimal_candles, "ATR", index=5) == 600

    @pytest.mark.usefixtures("minimal_candles")
    def test_nested_indicator_indexed(self, minimal_candles: List[Candle]):
        assert reading_by_index(minimal_candles, "NATR", index=5) == {"nested": 601}

    @pytest.mark.usefixtures("minimal_candles")
    def test_inner_nested_indicator_indexed(self, minimal_candles: List[Candle]):
        assert reading_by_index(minimal_candles, "NATR.nested", index=5) == 601

    @pytest.mark.usefixtures("minimal_candles")
    def test_subindicator(self, minimal_candles: List[Candle]):
        assert reading_by_index(minimal_candles, "SATR") == 2010

    @pytest.mark.usefixtures("minimal_candles")
    def test_nested_subindicator(self, minimal_candles: List[Candle]):
        assert reading_by_index(minimal_candles, "SSATR") == {"nested": 2011}

    @pytest.mark.usefixtures("minimal_candles")
    def test_inner_nested_subindicator(self, minimal_candles: List[Candle]):
        assert reading_by_index(minimal_candles, "SSATR.nested") == 2011

    @pytest.mark.usefixtures("minimal_candles")
    def test_subindicator_indexed(self, minimal_candles: List[Candle]):
        assert reading_by_index(minimal_candles, "SATR", index=5) == 610

    @pytest.mark.usefixtures("minimal_candles")
    def test_nested_subindicator_indexed(self, minimal_candles: List[Candle]):
        assert reading_by_index(minimal_candles, "SSATR", index=5) == {"nested": 611}

    @pytest.mark.usefixtures("minimal_candles")
    def test_inner_nested_subindicator_indexed(self, minimal_candles: List[Candle]):
        assert reading_by_index(minimal_candles, "SSATR.nested", index=5) == 611


@pytest.mark.usefixtures("minimal_candles")
def test_reading_count(minimal_candles: List[Candle]):
    assert reading_count(minimal_candles, "open") == 20


@pytest.mark.usefixtures("minimal_candles")
def test_reading_count_limited(minimal_candles: List[Candle]):
    assert reading_count(minimal_candles, "MinTR") == 10


@pytest.mark.usefixtures("minimal_candles")
def test_reading_as_list_exp(minimal_candles: List[Candle]):
    assert reading_as_list(minimal_candles, "ATR") == [
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


@pytest.mark.usefixtures("minimal_candles")
def test_reading_as_list_partial(minimal_candles: List[Candle]):
    assert reading_as_list(minimal_candles, "MinTR") == [
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


@pytest.mark.usefixtures("minimal_candles")
def test_reading_as_list_no_indicator(minimal_candles: List[Candle]):
    assert reading_as_list(minimal_candles, "FUCK") == [None] * 20


@pytest.mark.usefixtures("minimal_candles")
def test_reading_period(minimal_candles: List[Candle]):
    assert reading_period(minimal_candles, 5, "MinTR") is True


@pytest.mark.usefixtures("minimal_candles")
def test_reading_period_over(minimal_candles: List[Candle]):
    assert reading_period(minimal_candles, 15, "MinTR") is False


@pytest.mark.usefixtures("minimal_candles")
def test_reading_period_over_indexed(minimal_candles: List[Candle]):
    assert reading_period(minimal_candles, 5, "MinTR", 10) is False


class TestMergingCandlesTimeFrame:
    def test_collapse_candles_timeframe_empty(self):
        assert collapse_candles_timeframe([], "t10") == []

    @pytest.mark.usefixtures("candles", "candles_T5")
    def test_collapse_candles_first(self, candles: List[Candle], candles_T5: List[Candle]):
        collapsed_candles = collapse_candles_timeframe(candles, "T5")
        assert collapsed_candles[0] == candles_T5[0]

    @pytest.mark.usefixtures("candles", "candles_T5")
    def test_collapse_candles_second(self, candles: List[Candle], candles_T5: List[Candle]):
        collapsed_candles = collapse_candles_timeframe(candles, "T5")
        assert collapsed_candles[1] == candles_T5[1]

    @pytest.mark.usefixtures("candles", "candles_T5")
    def test_collapse_candles_last(self, candles: List[Candle], candles_T5: List[Candle]):
        collapsed_candles = collapse_candles_timeframe(candles, "T5")
        assert collapsed_candles[-1] == candles_T5[-1]

    @pytest.mark.usefixtures("candles", "candles_T5")
    def test_collapse_candles_t5(self, candles: List[Candle], candles_T5: List[Candle]):
        collapsed_candles = collapse_candles_timeframe(candles, "T5")
        assert collapsed_candles == candles_T5

    @pytest.mark.usefixtures("candles", "candles_T10")
    def test_collapse_candles_t10(self, candles: List[Candle], candles_T10: List[Candle]):
        collapsed_candles = collapse_candles_timeframe(candles, "T10")
        assert collapsed_candles == candles_T10

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

        collapsed_candles = collapse_candles_timeframe([data_input[0]], "T5")
        for candle in data_input[1:]:
            collapsed_candles.append(candle)
            collapsed_candles = collapse_candles_timeframe(collapsed_candles, "T5")

        assert collapsed_candles == expected

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

        collapsed_candles = collapse_candles_timeframe(data_input, "T5")

        collapsed_candles.append(copy.deepcopy(candles[20]))
        collapsed_candles = collapse_candles_timeframe(collapsed_candles, "T5")

        assert collapsed_candles == expected

    @pytest.mark.usefixtures("candles", "candles_T5")
    def test_collapse_candles_t5_appended(self, candles: List[Candle], candles_T5: List[Candle]):
        collapsed_candles = collapse_candles_timeframe([candles[0]], "T5")
        for candle in candles[1:]:
            collapsed_candles.append(candle)
            collapsed_candles = collapse_candles_timeframe(collapsed_candles, "T5")

        assert collapsed_candles == candles_T5

    @pytest.mark.usefixtures("candles", "candles_T10")
    def test_collapse_candles_t10_appended(self, candles: List[Candle], candles_T10: List[Candle]):
        collapsed_candles = collapse_candles_timeframe([candles[0]], "T10")
        for candle in candles[1:]:
            collapsed_candles.append(candle)
            collapsed_candles = collapse_candles_timeframe(collapsed_candles, "T10")

        assert collapsed_candles == candles_T10

    @pytest.mark.usefixtures("candles", "candles_T5")
    def test_collapse_candles_t5_multiple_collapse(
        self, candles: List[Candle], candles_T5: List[Candle]
    ):
        collapsed_candles = collapse_candles_timeframe(candles, "T5")
        assert collapsed_candles == candles_T5
        collapsed_candles = collapse_candles_timeframe(collapsed_candles, "T5")
        assert collapsed_candles == candles_T5
        collapsed_candles = collapse_candles_timeframe(collapsed_candles, "T5")
        assert collapsed_candles == candles_T5

    @pytest.mark.usefixtures("candles", "candles_T5")
    def test_collapse_candles_t5_mixed_neat(self, candles: List[Candle], candles_T5: List[Candle]):
        collapsed_candles = collapse_candles_timeframe(candles[:10], "T5")
        assert collapsed_candles == candles_T5[:2]
        collapsed_candles.extend(candles[10:])
        collapsed_candles = collapse_candles_timeframe(collapsed_candles, "T5")
        assert collapsed_candles == candles_T5

    @pytest.mark.usefixtures("candles", "candles_T5")
    def test_collapse_candles_t5_mixed_messy(
        self, candles: List[Candle], candles_T5: List[Candle]
    ):
        collapsed_candles = collapse_candles_timeframe(candles[:7], "T5")
        collapsed_candles.extend(candles[7:])
        collapsed_candles = collapse_candles_timeframe(collapsed_candles, "T5")

        assert collapsed_candles == candles_T5

    @pytest.mark.usefixtures("candles", "candles_T5")
    def test_collapse_candles_t5_missing_section(
        self, candles: List[Candle], candles_T5: List[Candle]
    ):
        cut_candles = candles[:5] + candles[-2:]
        result = collapse_candles_timeframe(cut_candles, "T5", False)
        assert result == [candles_T5[0], candles_T5[-1]]

    @pytest.mark.usefixtures("candles", "candles_T5")
    def test_collapse_candles_t5_missing_section_two(
        self, candles: List[Candle], candles_T5: List[Candle]
    ):
        cut_candles = candles[:5] + candles[10:15]
        result = collapse_candles_timeframe(copy.deepcopy(cut_candles), "T5", False)
        assert result == [candles_T5[0], candles_T5[2]]

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

        assert collapse_candles_timeframe(data_input, "T5", False) == expected

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
        assert collapse_candles_timeframe(data_input, "T5", False) == expected

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
        candles = []
        for candle in data_input:
            candles.append(candle)
            candles = collapse_candles_timeframe(candles, "T5", False)

        assert candles == expected


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

    assert fill_missing_candles(cut_candles, timedelta(minutes=5)) == [
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

    assert fill_missing_candles(cut_candles, timedelta(minutes=5)) == [
        candles_T5[0]
    ] + filler_candles + [candles_T5[-1]]


# @pytest.mark.usefixtures("candles", "candles_T5")
# def test_collapse_candles_t5_missing_section_fill_all(
#     candles: List[Candle], candles_T5: List[Candle]
# ):
#     cut_candles = candles[:5] + candles[-2:]

#     blank_candle = copy.deepcopy(candles_T5[0])
#     blank_candle.open = blank_candle.close
#     blank_candle.high = blank_candle.close
#     blank_candle.low = blank_candle.close
#     blank_candle.volume = 0

#     filler_candles = []
#     for i in range(99):
#         blank_candle.timestamp += timedelta(minutes=5)
#         filler_candles.append(copy.deepcopy(blank_candle))

#     assert collapse_candles_timeframe(cut_candles, "T5", True) == [
#         candles_T5[0]
#     ] + filler_candles + [candles_T5[-1]]


@pytest.mark.usefixtures("minimal_candles")
def test_candle_sum_reg_close(minimal_candles):
    assert candles_sum(minimal_candles, "close", length=2) == 19904


@pytest.mark.usefixtures("minimal_candles")
def test_candle_sum_reg_close_all(minimal_candles):
    assert candles_sum(minimal_candles, "close", length=9) == 104074


@pytest.mark.usefixtures("minimal_candles")
def test_candle_sum_reg_indicator(minimal_candles):
    assert candles_sum(minimal_candles, "ATR", length=3) == 5700


@pytest.mark.usefixtures("minimal_candles")
def test_candle_sum_reg_indicator_inverse_length(minimal_candles):
    assert candles_sum(minimal_candles, "ATR", length=3, index=-3) == 5100


@pytest.mark.usefixtures("minimal_candles")
def test_candle_sum_reg_indicator_insane_index(minimal_candles):
    assert candles_sum(minimal_candles, "ATR", length=3, index=100) is None


@pytest.mark.usefixtures("minimal_candles")
def test_candle_sum_reg_indicator_insane_index_and_length(minimal_candles):
    assert candles_sum(minimal_candles, "ATR", length=100, index=100) is None
