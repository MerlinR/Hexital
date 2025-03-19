# Features

Hexital is a powerful library for technical analysis, offering tools to calculate indicators and identify candlestick patterns from candle data. It also provides a range of utility functions to support custom analysis.

This page outlines Hexital's key features, offers a brief introduction to using them, and includes links to detailed guides for deeper exploration.

---

## Indicators

The core feature of Hexital is its technical analysis indicators, offering an ever-growing list designed to cater to a variety of trading strategies. All indicators are incrementally calculated and derived from the [Indicator][hexital.core.indicator.Indicator] class. They process data from a list of [Candles](features.md#candle); when a new candle is added, the indicator automatically updates with the latest calculated reading.

Each indicator is highly configurable, featuring options tailored to its specific purpose as well as general settings to enhance usability. This flexibility allows traders to fine-tune indicators for their unique requirements. Additionally, Hexital’s efficient incremental processing ensures minimal performance overhead, even when handling large datasets.

For a comprehensive overview of available indicators, configuration options, and examples, check out the [in-depth guide.](guides/indicators-indepth.md)

A full list is [available](indicator-catalogue.md)

### Indicator Chaining

Hexital allows you to chain indicators together seamlessly. In a chain, the output of one indicator can serve as the input for another, enabling automated, indefinite chaining of calculations.

This feature provides significant flexibility for creating custom indicators. For example, you can use an EMA to smooth the output of another indicator or incorporate indicators within other indicators to enhance their calculations.

A practical example is the calculation of the [Stochastic Oscillator (STOCH)][hexital.indicators.stoch.STOCH]. The `k` value of STOCH is used as the input for an SMA to compute the `d` value. Internally, this is implemented as the STOCH indicator chaining the SMA indicator, using its own `k` value as the input source.

### Custom Indicator's

All indicators in Hexital are implemented as dataclass objects, following a consistent and straightforward pattern. Most methods are inherited from the base [Indicator][hexital.core.indicator.Indicator] class, making it easy for users to create custom indicators. These custom indicators can be used individually or integrated into [Hexital][hexital.core.hexital.Hexital] as part of a trading strategy.

Below is an example of a custom indicator, which utilizes [Indicator chaining](features.md#indicator-chaining). This custom indicator, HighLowAverageSmoothed, calculates the average of the high and low values for each candle, then smooths the result using an EMA.

**Defining the Custom Indicator:**

```python linenums="1"
from dataclasses import dataclass, field

from hexital.core.indicator import Indicator, Managed
from hexital.indicators.ema import EMA


@dataclass(kw_only=True)
class HighLowAverageSmoothed(Indicator):
    _name: str = field(init=False, default="HLASmooth")

    def _generate_name(self) -> str:
        return f"{self._name}"

    def _initialise(self):
        self.add_managed_indicator("EMA", EMA(name="HLSmoothed", source="HLAS_raw", period=6))
        self.add_managed_indicator("HLAS_raw", Managed(name="HLAS_raw"))

    def _calculate_reading(self, index: int) -> float | dict | None:
        self.managed_indicators["HLAS_raw"].set_reading(
            (self.candles[index].high + self.candles[index].low) / 2
        )
        self.managed_indicators["EMA"].calculate_index(index)
        return self.reading("HLSmoothed")

```

**Using Custom Indicator:**

```python linenums="1"
from custom import HighLowAverageSmoothed
from hexital import Candle, Hexital

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

strategy = Hexital("Demo Strat", candles, [HighLowAverageSmoothed()])
strategy.calculate()
print(strategy.reading("HLASmooth"))

```

!!! info "Usage"
    Currently there is no Plugin ability for Indicator's to be auto picked up be `Hexital`, but can still be used.

---

## Timeframes

A unique feature of Hexital is its ability to effortlessly compress candles into different timeframes. This means you can work using 1-second candles which will be generating 5-minute candles and their corresponding indicator readings, which update dynamically as new candles are added.

Example:

```python linenums="1"
from hexital import EMA, Candle

# T5 being 5 minutes
my_ema = EMA(candles=candles, timeframe="T5")
my_ema.calculate()

# 1-second Candle stream
async with connect(data_stream) as websocket:
    async for message in websocket:
        candle_1s = await websocket.recv()
        my_ema.append(Candle.from_dict(candle_1s))

```

The `timeframe` attribute exists in all [Indicators][hexital.core.indicator.Indicator] and [Hexital][hexital.core.hexital.Hexital], using either [TimeFrame][hexital.utils.timeframe.TimeFrame], `strings`, `int` or `timedelta`.

!!! info "Compression"
    It should go without saying, it cannot take 5 Minute candle's and downgrade them into second Candles.

---

## Hexital

he [Hexital][hexital.core.hexital.Hexital] class is a foundational component of the library, designed to simplify and enhance the process of managing multiple indicators within a single, unified interface. It serves as a central hub, offering a streamlined way to configure, calculate, and analyse multiple indicators simultaneously, making it an essential tool for developing robust and scalable trading strategies.

One of Hexital’s key strengths is its ability to pass global configuration options to all the indicators it manages. This ensures consistency and reduces redundancy when working with large numbers of indicators or custom configurations. Additionally, the `Hexital` class allows for seamless integration of multiple timeframes, candlestick types, and chained indicators, making it highly versatile for a variety of trading use cases.

Beyond configuration, Hexital provides direct access to all indicator readings, enabling you to query the latest values, historical data, and trends with minimal effort. Whether you are working with simple moving averages or complex custom indicators, the Hexital class unifies their management and processing, ensuring your strategy remains organized and efficient.

It also supports the incremental calculation. Each appended candle triggers the calculation of the latest Candle across all associated indicators, ensuring your strategy remains up-to-date with the latest market data. This feature is particularly useful for live trading scenarios, where timely calculations are critical.

**Example:**

```python linenums="1"
from hexital import EMA, Supertrend, Candle, Hexital

strategy = Hexital("Demo Strat", [], [
        EMA(name="EMA_short",),
        Supertrend(name="supertrend"),
    ]
)

# Will run calculate on EMA and supertrend
strategy.calculate()

# Appends a new Candle, triggering all indicators to calculate new readings
strategy.append(Candle(
        open=12331.69,
        high=12542.540,
        low=12202.410,
        close=12536.019,
        volume=500,
    )
)
```

For a comprehensive overview of [Hexital][hexital.core.hexital.Hexital], configuration options, and examples, check out the [in-depth guide.](guides/hexital-indepth.md)

### Multi-Timeframes

As explained in [Timeframes](features.md#timeframes), Hexital allows you to compress candles into larger timeframes. This functionality extends to multiple indicators across different timeframes, all while requiring only a single set of candle data.

For example, if you are working using 1-second candles, you can generate:

- A 1-minute EMA
- A 5-minute SMA
- A 5-minute Supertrend
- A 1-hour EMA

This is achieved by appending the 1-second candles into a [Hexital][hexital.core.hexital.Hexital] object, which handles the timeframe conversions automatically.

**Example:**

```python linenums="1"
from hexital import EMA, SMA, Supertrend, Candle, Hexital
from datetime import timedelta

strategy = Hexital("Demo Strat", [], [
        EMA(name="EMA_short", period=14, timeframe="T1"),
        SMA(name="EMA_mid", period=20, timeframe=300),
        Supertrend(timeframe="T5"),
        EMA(name="EMA_long", timeframe=timedelta(hours=1)),
    ]
)

# 1-second Candle stream
async with connect(data_stream) as websocket:
    async for message in websocket:
        candle_1s = await websocket.recv()
        my_ema.append(Candle.from_dict(candle_1s))
```

---

## Candle

The [Candle][hexital.core.candle.Candle] class is a core object that the library expects as input. Candles can be created easily from `dicts` or `lists`.

Using a custom object for this OHLCV provides several advantages:

- Calculated reading's are stored within the Candle itself, and not the indicator that generated it.
- The Candle object includes many useful methods, such as `positive`, `negative`, `realbody` etc
- Supports merging Candle's, which is used when collapsing Candle Timeframes.
- The Candle class provides factory methods for easily generating Candle objects
- Cache's itself for support of altering it's [type](features.md#candlestick-type)

However, developers can choose to use the Candle object simply as an OHLCV (Open, High, Low, Close, Volume) object if they prefer.

```python linenums="1"
from hexital import Candle

print(Candle(
        open=12331.69,
        high=12542.540,
        low=12202.410,
        close=12536.019,
        volume=500,
    )
)
```

For a comprehensive overview of Candle's, configuration options, and examples, check out the [ guide.](guides/candles.md)

---

## Analysis

When developing trading strategies, quick and efficient access to indicator readings is essential. Hexital is designed to simplify this process by providing intuitive tools to retrieve and analyse the latest, previous, or a set of historical readings for any configured indicator. These tools streamline the workflow of building strategies and allow developers to focus on decision-making logic rather than low-level data handling.

The library ensures seamless integration of analysis functions into its architecture, allowing users to retrieve indicator readings and trends effortlessly. Whether you need to track a single indicator’s movement or analyse crossovers and other patterns between multiple indicators, Hexital provides the tools to handle these scenarios effectively.

**Using:**

```python linenums="1"
strategy = Hexital("Demo Strat", [], [
        EMA(name="EMA_short", period=14, timeframe="T1"),
        SMA(name="EMA_mid", period=20, timeframe=300),
        Supertrend(timeframe="T5"),
        EMA(name="EMA_long", timeframe=timedelta(hours=1)),
    ]
)
```

**Reading latest:**

```python linenums="8"
strategy.reading("EMA_long")
```

**Reading Prevouse:**

```python linenums="9"
strategy.prev_reading("EMA_mid")
```

**All Readings:**

```python linenums="10"
strategy.readings("Supertrend_7")
```

### Movement functions

In addition, Hexital offers a powerful suite of movement functions designed to detect and analyse trends and patterns in indicator readings. These functions integrate seamlessly with [Indicator][hexital.core.indicator.Indicator] and [Hexital][hexital.core.hexital.Hexital] objects, making them indispensable tools for strategy development. Whether you're evaluating trends, identifying critical market movements, these functions provide an efficient and straightforward way to extract actionable insights.

Movement functions are designed to detect specific behaviors or changes in indicator readings over time. They simplify the implementation of complex trading logic, enabling strategies to react dynamically to market conditions. These functions also fully support multi-timeframe analysis, ensuring that indicators operating on different candlestick timeframes can be analysed together without any additional configuration.

**Using:**

```python linenums="1"
strategy = Hexital("Demo Strat", [], [
        EMA(name="EMA_short", period=14, timeframe="T1"),
        SMA(name="EMA_mid", period=20, timeframe=300),
        Supertrend(timeframe="T5"),
        EMA(name="EMA_long", timeframe=timedelta(hours=1)),
    ]
)
```

**Long EMA is rising:**

```python linenums="8"
from hexital.analysis.movement import rising
rising(strategy, "EMA_long", length=8)
```

**Highest EMA_mid has been in last 100 Candles:**

```python linenums="10"
from hexital.analysis.movement import highest
crossover(highest, "EMA_mid", length=100)
```

**Short EMA crossed Long EMA:**

```python linenums="12"
from hexital.analysis.movement import crossover
crossover(strategy, "EMA_short", "Supertrend_7", length=8)
```

!!! info "Analysis over Timeframes"
    Note that analysis such as crossover will work correctly when using them across multiple TimeFrames.

A full list is [available](analysis-catalogue.md)

---

## Patterns

Hexital goes beyond Indicators by offering robust pattern detection functions to identify common candlestick patterns, such as [Doji][hexital.analysis.patterns.doji], [Dojistar][hexital.analysis.patterns.dojistar], [Hammer][hexital.analysis.patterns.hammer], and more. These functions are easy to use, versatile, and allow configuration like specifying a lookback period to analyse recent candles.

Hexital’s pattern detection is a powerful tool for spotting trends and reversals, and it pairs effectively with Indicators and movement functions. These pattern detection functions are designed to be simple and easy to use, as shown below:

**Using:**

```python linenums="1"
from hexital import EMA, Candle

# T5 being 5 minutes
my_ema = EMA(candles=candles, timeframe="T5")
my_ema.calculate()
```

**Doji:**

```python linenums="6"
from hexital.analysis.patterns import doji

print(doji(my_ema.candles))
```

**Doji occurred last 10 Candles:**

```python linenums="9"
from hexital.analysis.patterns import doji

print(doji(my_ema.candles, lookback=10))
```

!!! info "Pattern Functions"
    Note all pattern functions use a `List[Candle]` and can accept an optional `lookback` parameter to check for the pattern in the last N candles.

A full list is [available](candle-pattern-catalogue.md)

### Automatically calculate patterns

In addition to pattern detection functions, Hexital features a unique [amorph][hexital.indicators.amorph.Amorph] Indicator class. The Amorph indicator does not perform any calculations on its own. Instead, it is given a function (such as a pattern detection function) that runs for each appended candle. The output of that function becomes the reading of the indicator. This feature provides a special use case where users can treat functions as if they were indicators, and have them run automatically with minimal setup.

**Example:**

```python linenums="9"
from hexital.analysis.patterns import doji
from hexital.indicators.amorph import Amorph

# Use the 'doji' pattern detection function as an indicator
test = Amorph(analysis=patterns.doji, candles=candles)
test.calculate()
```

For a comprehensive overview of amorph, configuration options, and examples, check out the [in-depth guide.](guides/custom-indicator.md#amorph)

---

## Candlestick Types - BETA

The library also provides a way to convert traditional OHLCV Candles into different types of Candlesticks. This allows your inputted Candles to be automatically converted into chart types like [Heikin-Ashi][hexital.candlesticks.heikinashi.HeikinAshi], prior to any Indicator calculations. As a result, all Indicator readings will be based on the newly converted Candlestick type. This approach works seamlessly with other configuration options like Timeframes.

**Example:**

```python linenums="1"
from hexital import EMA, Candle
from hexital.candlesticks.heikinashi import HeikinAshi

# EMA is calculated on the Heikin-Ashi converted Candles
my_ema = EMA(candles=candles, candlestick=HeikinAshi)
my_ema.calculate()
```

A full list is [available](candlesticks-catalogue.md)

---

## Serialisation

The design of Hexital allows for very easy serialisation, this is due to the way the readings are managed. Rather than indicator reading's being stored within the [Indicator][hexital.core.indicator.Indicator] or [Hexital][hexital.core.hexital.Hexital], they are stored within the [Candles][hexital.core.candle.Candle] themselves.

This means you can simply store the [Candles][hexital.core.candle.Candle] list elsewhere, such as DataBase, CSV or some cache. Which will keep all the readings and calculation data required by the [Indicator][hexital.core.indicator.Indicator] or [Hexital][hexital.core.hexital.Hexital] stored alongside the given [Candles][hexital.core.candle.Candle].

### Serialisation

Below is a basic example of saving the Candle's alongside it's readings and calculation data. Whereby we simply save it into a CSV file.

```python linenums="1"
TODO
```

### Deserialisation

Deserialise is a simply process of reusing the given data to regenerate the Candle's.

```python linenums="1"
TODO
```
