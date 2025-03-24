from hexital.utils.indexing import absindex, valid_index


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
    assert absindex(10, 10) == 9


def test_absindex_basic_negative():
    assert absindex(-1, 10) == 9


def test_absindex_basic_negative_two():
    assert absindex(-4, 10) == 6


def test_absindex_basic_negative_invalid():
    assert absindex(-20, 10) == 9
