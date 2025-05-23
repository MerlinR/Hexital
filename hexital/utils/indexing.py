def absindex(index: int | None, length: int) -> int:
    """Ensure's Index is a positive index, -1 == length-1"""
    if index is None:
        return length - 1
    if not valid_index(index, length):
        return length - 1
    if index < 0:
        return length + index
    return index


def valid_index(index: int | None, length: int) -> bool:
    if index is None:
        return False
    if not length > index >= -length:
        return False
    return True
