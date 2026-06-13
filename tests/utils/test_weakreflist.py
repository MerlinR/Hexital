import gc

from hexital.utils.weakreflist import WeakList


class Box:
    def __init__(self, value):
        self.value = value

    def __eq__(self, other):
        return isinstance(other, Box) and self.value == other.value

    def __repr__(self):
        return f"Box({self.value!r})"


def test_init_append_and_getitem():
    items = [Box(1), Box(2)]
    weak_list = WeakList(items)

    assert weak_list[0] == items[0]
    assert weak_list[:] == items


def test_flush_and_len_after_gc():
    item = Box(1)
    weak_list = WeakList([item])

    del item
    gc.collect()

    assert len(weak_list) == 0
    assert list(weak_list) == []


def test_reset_clears_refs():
    weak_list = WeakList([Box(1), Box(2)])
    weak_list.reset()
    assert len(weak_list) == 0
    assert weak_list[:] == []


def test_eq_and_repr():
    items = [Box(1), Box(2)]
    weak_list = WeakList(items)

    assert weak_list == items
    assert weak_list != "nope"
    assert "WeakList" in repr(weak_list)


def test_setitem_and_delitem():
    items = [Box(1), Box(2), Box(3)]
    weak_list = WeakList(items)

    replacement = Box(9)
    weak_list[1] = replacement
    assert weak_list[1] == replacement

    replacements = [Box(7), Box(8)]
    weak_list[:2] = replacements
    assert [box.value for box in weak_list[:2]] == [7, 8]

    del weak_list[0]
    assert [box.value for box in weak_list] == [8, 3]


def test_extend_insert_pop_remove_reverse_contains():
    first = Box(1)
    second = Box(2)
    third = Box(3)
    inserted = Box(9)
    weak_list = WeakList([first])

    weak_list.extend([second, third])
    weak_list.insert(1, inserted)
    assert inserted in weak_list

    popped = weak_list.pop(1)
    assert popped == inserted

    weak_list.remove(second)
    weak_list.reverse()
    assert [box.value for box in weak_list] == [3, 1]


def test_add_and_iadd():
    left_items = [Box(1)]
    right = [Box(2), Box(3)]
    left = WeakList(left_items)

    combined = left + right
    assert [box.value for box in combined] == [1, 2, 3]

    left += right
    assert [box.value for box in left] == [1, 2, 3]


def test_mul_and_imul():
    items = [Box(1), Box(2)]
    weak_list = WeakList(items)

    doubled = weak_list * 2
    assert [box.value for box in doubled] == [1, 2, 1, 2]

    weak_list *= 2
    assert [box.value for box in weak_list] == [1, 2, 1, 2]
