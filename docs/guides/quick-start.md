
# Quick Start

## Introduction

 This page is a quick start guide on generating your first technical indicator using Hexital, as well as using it to generate a set of technical indicators with some useful common situations and features.

---

## Creating Candles

Hexital use's it's own Candle object used for generating technical indicator readings, these are a core part of Hexital and can therefore be created in several different ways.

=== "Automatically when appending"
    To simplify the process of converting your data into [Candle][hexital.core.candle.Candle] objects used by Hexital the Indicator objects can accept a variety of formats and convert them for you. The format's it can accept are `Lists`, `Dicts` which are also explained here.

    ```python linenums="1"
    from hexital import EMA, Candle

    my_ema = EMA(candles=[])
    # EMA Indicator accepting a list format which will be converted to a Candle object prior to calculation.
    my_ema.append([datetime(2023, 12, 1, 14, 30), 1.2345, 1.2500, 1.2300, 1.2450, 10000])

    # EMA Indicator accepting a dict format which will be converted to a Candle object prior to calculation.
    my_ema.append(
        Candle.from_dict(
            {
                "open": 1.2345,
                "high": 1.2500,
                "low": 1.2300,
                "close": 1.2450,
                "volume": 10000,
                "timestamp": datetime(2023, 12, 1, 14, 30),
            }
        )
    )
    ```

=== "Directly"
    You can create a [Candle][hexital.core.candle.Candle] instance by providing its required attributes: `open`, `high`, `low`, `close`, and `volume`.
    
    ```python linenums="1"
    from datetime import datetime
    from hexital import Candle

    # Create a Candle with explicit values
    candle = Candle(
        open=1.2345,
        high=1.2500,
        low=1.2300,
        close=1.2450,
        volume=10000,
        timestamp=datetime(2023, 12, 1, 14, 30),
        timeframe="1h"
    )

    print(candle)
    # Output: Candle(open=1.2345, high=1.25, low=1.23, close=1.245, volume=10000)
    ```
=== "From List"
    You can use the [from_list][hexital.core.candle.Candle.from_list] class method to create a [Candle][hexital.core.candle.Candle] from a list containing the following attributes in order:

    `[timestamp (optional), open, high, low, close, volume, timeframe (optional)]`

    ```python linenums="1"
    from datetime import datetime
    from hexital import Candle
    candle_data = [datetime(2023, 12, 1, 14, 30), 1.2345, 1.2500, 1.2300, 1.2450, 10000, "1h"]

    # Create a Candle using from_list
    candle = Candle.from_list(candle_data)

    print(candle)
    # Output: Candle(open=1.2345, high=1.25, low=1.23, close=1.245, volume=10000)
    ```

    !!! info "from_lists"
        Another method called [from_lists][hexital.core.candle.Candle.from_lists] which accept's a list of list's to convert, returning a List[Candle].

=== "From Dict"
    You can create a [Candle][hexital.core.candle.Candle] instance from a dictionary by using the [from_dict][hexital.core.candle.Candle.from_dict] class method. This is especially useful when working with JSON data or API responses.

    ```python linenums="1"
    from datetime import datetime
    from hexital import Candle

    candle_dict = {
        "open": 1.2345,
        "high": 1.2500,
        "low": 1.2300,
        "close": 1.2450,
        "volume": 10000,
        "timestamp": datetime(2023, 12, 1, 14, 30),
        "timeframe": "1h",
    }
    candle = Candle.from_dict(candle_dict)
    print(candle)
    # Output: Candle(open=1.2345, high=1.25, low=1.23, close=1.245, volume=10000)
    ```

     !!! info "from_dicts"
        Another method called [from_dicts][hexital.core.candle.Candle.from_dicts] which accept's a list of dict's to convert, returning a List[Candle].
=== "From CSV"
    [TODO](https://github.com/MerlinR/Hexital/issues/29)
=== "From Pandas"

    Panda dataframes can be converted using dataframes [`to_dict`](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_dict.html) method and feeding the result into the [Candle][hexital.core.candle.Candle] [from_dicts][hexital.core.candle.Candle.from_dicts] class method.

    ```python
    from hexital import EMA, Candle
    import pandas as pd

    df = pd.read_csv("path/to/symbol.csv", sep=",")
    candles = Candle.from_dicts(df.to_dict("records"))

    my_ema = EMA(candles=candles)
    my_ema.calculate()

    print("EMA reading:", my_ema.reading())
    ```

---

## EMA Indicator

The purpose of Hexital is to incrementally create technical indicator readings, therefore it's made to be relatively simple.
Below is example's of using Hexital to create an EMA indicator from a list of `dict` Candles. As well as some common and useful configurations.

```python linenums="1"
from hexital import EMA, Candle
from datetime import timedelta

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

my_ema = EMA(name="EMA_Short", candles=candles, period=3, candle_life=timedelta(hours=2))
my_ema.calculate()

print("Latest EMA reading:", my_ema.reading())  # 8408.7552
```

### EMA period
In the given example the length/period of the EMA indicator is 3. This is of course configurable.
```python linenums="19"
my_ema = EMA(name="EMA_Short", candles=candles, period=3, candle_life=timedelta(hours=2))
```


### Appending new Candle
Hexital is designed to be constantly receiving and updating it's Candle list and TA readings, therefore they can easily [append][hexital.core.indicator.Indicator] new candles in a variety of formats; As explained in the [Candle](/Hexital/guides/quick-start#candle) section.
```python linenums="23"

# Append new Candle
my_ema.append(Candle.from_dict({'open': 19723, 'high': 4837, 'low': 11631, 'close': 6231, 'volume': 38993}))
print("EMA reading:", my_ema.reading())  # 7319.8776
```

!!! info "Auto calculation"
    We dont need to call calculation method as it's done automatically on append.


### Indicator candle_life
All indicators have the configuration option `candle_life`, this is optional configuration which is useful for very large everygrowing set of Candle's. This attribute will automatically cull the list of Candle's it stores based on it's age, in this case once a Candle is 2 hours old it will be removed.

```python linenums="19"
my_ema = EMA(name="EMA_Short", candles=candles, period=3, candle_life=timedelta(hours=2))
```

!!! info "Candle life"
    Extremely useful for managing memory constraints, but note you will also lose the TA readings alongside the Candle's.


### EMA Indicator name
We manually selected the Indicator name, this is optional, however recommended when dealing with many indicators, the default naming is generated based on the TA name and the period set. E.G `EMA_3` would otherwise be generated.
```python linenums="19"
my_ema = EMA(name="EMA_Short", candles=candles, period=3, candle_life=timedelta(hours=2))
```


###  Analysis EMA for rising trend
You can also directly use one of Hexital's built in analysis functions to handle simple movements calculations, for example to check if the EMA value we are generating is rising or falling.

```python linenums="28"
from hexital.analysis import rising

print("EMA Rising:" rising(my_ema, "EMA_3", length=8)) # False
```

---

## Hexital - Indicator Grouping

A single indicator is useful but no trading strategy is built using a single one, to avoid haivng to create and manage and appending to several indicators. Therefore Hexital library has the [Hexital][hexital.core.hexital.Hexital] object, which is designed for managing multiple indicators easily, by having one set of candle's which is used for multiple indicator's they will all automatically be given new Candle and re-calculated; as if managing one Indicator.

This example is using Hexital to manage [WMA][hexital.indicators.wma.WMA] and [EMA][hexital.indicators.ema.EMA] in one [Hexital][hexital.core.hexital.Hexital] object, updating and calculating both indicators from appending a single Candle.

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

strategy = Hexital("Demo Strat", candles,
    candle_life=timedelta(hours=2)
    [
        WMA(name="WMA", period=8),
        EMA(period=3, candle_life=timedelta(hours=1)),
    ]
)
strategy.calculate()

print("EMA reading:", strategy.reading("EMA_3")) # 8408.7552
print("WMA reading:", strategy.reading("WMA")) # 9316.4722

```

All the configuration that is available to the `EMA` indicator is still available while being used within the Hexital object.

!!! warning "EMA naming"
    EMA was not given a specific name, the name is therefore generated based of the Indicator name(*EMA*) and Period(*3*).
    Which us why in `strategy` it's called as `EMA_3`. This changes if the period changes.


### Appending new Candle
We can append a `Candle` to Hexital which is then used for all Indicator's, the EMA and WMA value's are again automatically calculated on append.

```python linenums="28"

# Append new Candle
strategy.append(
    Candle.from_dict({"open": 19723, "high": 4837, "low": 11631, "close": 6231, "volume": 38993})
)
# New readings from both indicators using new Candle
print("EMA reading:", strategy.reading("EMA_3"))  # 7319.8776
print("WMA reading:", strategy.reading("WMA"))  # 8934.9722
```

!!! info "Auto calculation"
    We dont need to call calculation method as it's done automatically on append.

### Hexital's own configuration (candle_life)
Notice that the Hexital object has it's own `candle_life` attribute. The purpose of this is a global way to set configurations within the Hexital Indicators. Therefore **all** indicators that exist within this strategy object will inherit a `candle_life` value of 2 hours. *However* the EMA TA has it's own `candle_life` attribute which will take precedence over the Hexital's.

The purpose is you can set a global configuration for all indicators without having to add it to each TA manually.

```python linenums="17"
strategy = Hexital("Demo Strat", candles,
    candle_life=timedelta(hours=2)
    [
        WMA(name="WMA", period=8),
        EMA(period=3, candle_life=timedelta(hours=1)),
    ]
)
```


###  Analysis for EMA and WMA Crossing
You can also pass the Hexital object into one of Hexital's built in analysis functions, for example to check if the EMA value we are generating has crossed over the WMA.

```python linenums="30"
from hexital.analysis import cross

print("EMA Crossed WMA:" cross(strategy, "EMA_3", "WMA")) # False
```
!!! info "EMA Name"
    The EMA_3 name is the generated name, if you decide to alter to period of this EMA to say 6; the name would change to match resulting in these call's failing. This is why it's best practice to manually choose a name when creating a indicator.

!!! info "Analysis methods"
    We can replace `cross` with `crossover` or `crossunder` for specific direction.

---

