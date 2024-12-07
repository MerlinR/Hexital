
# Quick Start

## Introduction

## EMA Indicator

An example of using Hexital to create an EMA indicator from a list of `dict` Candles.

```python linenums="1"
from hexital import EMA, Candle

my_candles = [
    {"open": 17213, "high": 2395, "low": 7813, "close": 3615, "volume": 19661},
    {"open": 1301, "high": 3007, "low": 11626, "close": 19048, "volume": 28909},
    {"open": 12615, "high": 923, "low": 7318, "close": 1351, "volume": 33765},
    {"open": 1643, "high": 16229, "low": 17721, "close": 212, "volume": 3281},
    {"open": 424, "high": 10614, "low": 17133, "close": 7308, "volume": 41793},
    {"open": 4323, "high": 5858, "low": 8785, "close": 8418, "volume": 34913},
    {"open": 13838, "high": 13533, "low": 4830, "close": 17765, "volume": 586},
    {"open": 14373, "high": 18026, "low": 7844, "close": 18798, "volume": 25993},
    {"open": 12382, "high": 19875, "low": 2853, "close": 1431, "volume": 10055},
    {"open": 19202, "high": 6584, "low": 6349, "close": 8299, "volume": 13199},
]
# Convert Basic candles
candles = Candle.from_dicts(my_candles)

my_ema = EMA(candles=candles, period=3)
my_ema.calculate()

print("Latest EMA reading:", my_ema.reading())  # 8408.7552
```


### Appending new Candle
```python linenums="23"

# Append new Candle
my_ema.append(Candle.from_dict({'open': 19723, 'high': 4837, 'low': 11631, 'close': 6231, 'volume': 38993}))
print("EMA reading:", my_ema.reading())  # 7319.8776
```

!!! info "EMA naming"
    The latest EMA value is automatically calculated on append.

###  Analysis EMA for rising trend
Hexital has several built in analysis functions to handle simple candle movements calculations.

```python linenums="28"
from hexital.analysis import rising

print("EMA Rising:" rising(my_ema, "EMA_3", length=8)) # False
```

---

## Hexital - Indicator Grouping

[Hexital][hexital.core.hexital.Hexital] is designed for managing multiple indicators, by having one set of candle's which is used for a list of indicator's they will all automatically be given new Candle and re-calculated.

This example of Hexital having [WMA][hexital.indicators.wma.WMA] and [EMA][hexital.indicators.ema.EMA] in one [Hexital][hexital.core.hexital.Hexital] object, and updating and calculating both indicators from appending a single Candle.

```python linenums="1"
from hexital import EMA, WMA, Candle, Hexital

my_candles = [
    {"open": 17213, "high": 2395, "low": 7813, "close": 3615, "volume": 19661},
    {"open": 1301, "high": 3007, "low": 11626, "close": 19048, "volume": 28909},
    {"open": 12615, "high": 923, "low": 7318, "close": 1351, "volume": 33765},
    {"open": 1643, "high": 16229, "low": 17721, "close": 212, "volume": 3281},
    {"open": 424, "high": 10614, "low": 17133, "close": 7308, "volume": 41793},
    {"open": 4323, "high": 5858, "low": 8785, "close": 8418, "volume": 34913},
    {"open": 13838, "high": 13533, "low": 4830, "close": 17765, "volume": 586},
    {"open": 14373, "high": 18026, "low": 7844, "close": 18798, "volume": 25993},
    {"open": 12382, "high": 19875, "low": 2853, "close": 1431, "volume": 10055},
    {"open": 19202, "high": 6584, "low": 6349, "close": 8299, "volume": 13199},
]
candles = Candle.from_dicts(my_candles)

strategy = Hexital("Demo Strat", candles, [
    WMA(name="WMA", period=8),
    EMA(period=3),
])
strategy.calculate()

print("EMA reading:", strategy.reading("EMA_3")) # 8408.7552
print("WMA reading:", strategy.reading("WMA")) # 9316.4722

```

!!! warning "EMA naming"
    EMA was not given a specific name, the name is therefore generated based of the Indicator name(*EMA*) and Period(*3*).
    Which us why in `strategy` it's called as `EMA_3`.


### Appending new Candle
We can append a `Candle` to Hexital which is then used for all Indicator's, the EMA and WMA value's are again automatically calculated on append.

```python linenums="23"

# Append new Candle
strategy.append(
    Candle.from_dict({"open": 19723, "high": 4837, "low": 11631, "close": 6231, "volume": 38993})
)
# New readings from both indicators using new Candle
print("EMA reading:", strategy.reading("EMA_3"))  # 7319.8776
print("WMA reading:", strategy.reading("WMA"))  # 8934.9722
```

###  Analysis for EMA and WMA Crossing
The several built in analysis functions can handle check across multiple indicator.

```python linenums="30"
from hexital.analysis import cross

print("EMA Crossed WMA:" cross(my_ema, "EMA_3", "WMA")) # False
```

!!! info "Analysis methods"
    We can replace `cross` with `crossover` or `crossunder` for specific direction.

---

---

## Creating Candles
=== "From Lists"
    Fuck
=== "From Dicts"
    you
=== "From CSV"
    bitch
=== "From Pandas"

    Panda dataframes can be converted using dataframes [`to_dict`](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_dict.html) method and feeding the result into the Candle [from_dicts][hexital.core.candle.Candle.from_dicts] class method.

    ```python
    from hexital import EMA, Candle
    import pandas as pd

    df = pd.read_csv("path/to/symbol.csv", sep=",")
    candles = Candle.from_dicts(df.to_dict("records"))

    my_ema = EMA(candles=candles)
    my_ema.calculate()

    print("EMA reading:", my_ema.reading())
    ```