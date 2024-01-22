from hexital.utils.indexing import absindex, round_values, valid_index


def test_round_values_simple():
    assert round_values(100.696666) == 100.6967


def test_round_values_simple_int():
    assert round_values(100) == 100


def test_round_values_none():
    assert round_values(None) is None


def test_round_values_dict_simple():
    assert round_values({"one": 100.696666}) == {"one": 100.6967}


def test_round_values_dict_mixed():
    assert round_values({"one": 100.696666, "nada": None}) == {
        "one": 100.6967,
        "nada": None,
    }


def test_valid_index():
    assert valid_index(1, 100) is True


def test_valid_index_valid_empty_length():
    assert valid_index(0, 0) is False


def test_valid_index_invalid():
    assert valid_index(100, 1) is False


def test_valid_index_invalid_none():
    assert valid_index(None, 1) is False


def test_valid_index_valid_negative():
    assert valid_index(-1, 1) is True


def test_valid_index_valid_negative_empty_length():
    assert valid_index(-1, 0) is False


def test_absindex_basic():
    assert absindex(1, 10) == 1


def test_absindex_basic_two():
    assert absindex(9, 10) == 9


def test_absindex_basic_invalid():
    assert absindex(10, 10) is None


def test_absindex_basic_negative():
    assert absindex(-1, 10) == 9


def test_absindex_basic_negative_two():
    assert absindex(-4, 10) == 6


def test_absindex_basic_negative_invalid():
    assert absindex(-20, 10) is None
