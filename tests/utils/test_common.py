from hexital.utils.common import round_values


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
