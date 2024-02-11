from .movement import (  # noqa F401
    cross,
    crossover,
    crossunder,
    falling,
    highest,
    highestbar,
    lowest,
    lowestbar,
    mean_falling,
    mean_rising,
    negative,
    positive,
    rising,
    value_range,
)
from .patterns import doji, hammer  # noqa F401

MOVEMENT_MAP = {
    "cross": cross,
    "crossover": crossover,
    "crossunder": crossunder,
    "falling": falling,
    "highest": highest,
    "highestbar": highestbar,
    "lowest": lowest,
    "lowestbar": lowestbar,
    "mean_falling": mean_falling,
    "mean_rising": mean_rising,
    "negative": negative,
    "positive": positive,
    "rising": rising,
    "value_range": value_range,
}

PATTERN_MAP = {
    "doji": doji,
    "hammer": hammer,
}
