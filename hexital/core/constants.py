NESTED_DELI = "."


def split_nested_name(name: str) -> tuple[str, str | None]:
    """Split ``indicator{nested}field`` into indicator name and nested field."""
    if NESTED_DELI not in name:
        return name, None
    main_name, nested_name = name.split(NESTED_DELI, 1)
    return main_name, nested_name

def get_main_name(name: str) -> str:
    """Get the main name from an indicator name."""
    if NESTED_DELI not in name:
        return name
    return split_nested_name(name)[0]

def get_nested_name(name: str) -> str:
    """Get the nested name from an indicator name."""
    if NESTED_DELI not in name:
        return name
    return split_nested_name(name)[1]

def join_nested_name(indicator_name: str, nested_name: str) -> str:
    """Join an indicator name with a nested reading field."""
    return f"{indicator_name}{NESTED_DELI}{nested_name}"
