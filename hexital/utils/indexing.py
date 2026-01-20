def absindex(index: int | None, length: int) -> int:
    """Ensure's Index is a positive index, -1 == length-1"""
    if index is None or index < -length or index >= length:
        return length - 1
    return index if index >= 0 else length + index


def valid_index(index: int | None, length: int) -> bool:
    if index is None or not length > index >= -length:
        return False
    return True
