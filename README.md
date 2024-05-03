# Hexital - Incremental Technical Analysis Library

[![license](https://img.shields.io/github/license/merlinr/hexital)](#license)
[![Python Version](https://img.shields.io/pypi/pyversions/hexital?style=flat)](https://pypi.org/project/hexital/)
[![PyPi Version](https://img.shields.io/pypi/v/hexital?style=flat)](https://pypi.org/project/hexital/)
[![Package Status](https://img.shields.io/pypi/status/hexital?style=flat)](https://pypi.org/project/hexital/)
![PyPI - Downloads](https://img.shields.io/pypi/dm/hexital?color=%2332c955)
![GitHub Repo stars](https://img.shields.io/github/stars/MerlinR/Hexital?style=flat)
[![Unit Tests - Master](https://github.com/MerlinR/Hexital/actions/workflows/unit_test.yaml/badge.svg?branch=master)](https://github.com/MerlinR/Hexital/actions/workflows/unit_test.yaml)
[![Unit Tests - Dev](https://github.com/MerlinR/Hexital/actions/workflows/unit_test.yaml/badge.svg?branch=development)](https://github.com/MerlinR/Hexital/actions/workflows/unit_test.yaml)

# `Beta`

Note: Hexital is in Beta, all Major features are implemented and not expected to have drastic changes.

# Hexital

`Hexital` is a Python library designed for technical analysis in financial markets, offering a range of indicators commonly used in trading strategies. What sets Hexital apart is its innovative approach to computation, specifically tailored for real-time or iterative applications.

While libraries like [Pandas-TA](https://github.com/twopirllc/pandas-ta) excel at generating indicators for large datasets, they often struggle with real-time or incremental data processing due to their reliance on recalculating the entire input vector. This inefficiency can significantly impact speed, as each new data point triggers a full recalculation of all indicators.

`Hexital` addresses this issue by employing an incremental computation method. Rather than reevaluating all data points, it selectively computes only the new or missing indicator values. This optimized approach ensures that generating new indicator values requires constant time complexity O(1), a stark contrast to the linear time complexity (O(n)) or worse exhibited by other libraries.

With Hexital, users can enjoy swift and efficient computation of indicators, making it ideal for applications requiring real-time analysis or iterative data processing.

## Features

### Indicators

Hexital offers a diverse range of indicators for technical analysis. These can be utilized individually to compute a single indicator or, with the Hexital class, multiple indicators can be automatically calculated using an incremental candle list, which is easily parsed.

### Candlestick Patterns

Hexital supports the detection of candle patterns, such as Doji, among others. This functionality can be easily accessed by calling the Pattern function with the candle data, or it can be automatically computed alongside other indicators.

### Candlestick Types

Hexital provides the capability to automatically convert candlesticks from the standard type into alternative formats, such as 'Heikin-Ashi'. Prior to generating indicators, candlesticks are automatically converted to the desired type, enabling indicator calculations on this new candlestick type. This feature seamlessly integrates with all other functionalities.

### Multi-Timeframes

Hexital boasts a key feature of supporting indicator and pattern computation on multiple candle timeframes using a single set of candles. For example, an indicator can be applied to second candlesticks to calculate EMA on 1m or 10m candlesticks. The indicator automatically merges these candles into the required timeframes and computes the indicator value.

This functionality can also be leveraged within the `Hexital` class, enabling the automatic computation of multiple incremental indicators and patterns across multiple timeframes by appending a single candle of any timeframe. For instance, by appending 1m candles into Hexital, you can automatically compute an RSI using 5-minute candles and an EMA using 10-minute candles, all while only adding 1m candlesticks.

Example:

```python
stratergy = Hexital("Test Stratergy", candlesticks_1m, [RSI(timeframe="T5"), EMA(timeframe=TimeFrame.MINUTE10)])
```

### Candlestick Movements

Hexital includes built-in candle utility methods for detecting movements such as Rising Candles and indicator crossovers. These methods are designed to simplify the process of analyzing candle data and common features. Many of these functionalities are inspired by those found in Pine Scripting.

## Indicators

- Average Directional Index(ADX)
- Aroon
- Average True Range (ATR)
- Bollinger Bands (BBANDS)
- Counter
- Donchian Channels (donchian)
- Exponential Moving Average (EMA)
- High Low Average
- Hull Moving Average (HMA)
- Keltner Channel (KC)
- Moving Average Convergence/Divergence (MACD)
- On Balance Volume (OBV)
- Relative Moving Average (RMA)
- Rate of Change (ROC)
- Relative strength index (RSI)
- Simple Moving Average(SMA)
- Standard Deviation (STDEV)
- Stochastic Oscillator (STOCH)
- Supertrend
- True Range (TR)
- True Strength Index (TSI)
- Volume Weighted Average Price (VWAP)
- Volume Weighed Moving Averge (VWMA)
- Weighed Moving Average (WMA)

## Candlestick Patterns

Simple useful Candle pattern recognition, such as Doji, hammer, etc

- Doji
- Dojistar
- Hammer
- Inverted Hammer

## Candlestick Types

Hexital can also automatically convert Candlesticks into specific types, such as:

- Heikin-Ashi

## Candlestick Movements

Simple useful Candle Anaylsis methods such as those in [Pine Scripting](https://www.tradingview.com/pine-script-reference/v5/)

- Positive/Negative Candle
- Rising/Falling Indicator
- Mean Based Rising/Falling Indicator
- Highest/Lowest Indicator (Value)
- HighestBar/LowestBar Indicator (Offset how far back)
- Indicator Cross
- Indicator CrossOver/CrossUnder

## Installation

### Stable

Pip and pypi package version is the latest stable version.

```bash
pip install hexital
```

## Latest

In case you want to install the latest development version from the repo.

```bash
pip install git+https://github.com/merlinr/hexital.git@development
```

## Usage

### Single Indicator

```python
from hexital import EMA, Candle
from hexital.analysis import movement
import pandas as pd

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
# Or directly from a Numpy Dataframe
# df = pd.read_csv("path/to/symbol.csv", sep=",")
# candles = Candle.from_dicts(df.to_dict("records"))

print("Indicator name:", my_ema.name)  # EMA_3
print("Has reading:", my_ema.has_reading)  # True
print("Latest EMA reading:", my_ema.reading())  # 8408.7552
print("All EMA readings:", my_ema.as_list())
# [None, None, 8004.6667, 4108.3333, 5708.1667, 7063.0833, 12414.0416, 15606.0208, 8518.5104, 8408.7552]

# Add new
my_ema.append(Candle.from_dict({'open': 19723, 'high': 4837, 'low': 11631, 'close': 6231, 'volume': 38993}))
print("EMA readings after appending new candle:", my_ema.as_list())
 # [None, None, 8004.6667, 4108.3333, 5708.1667, 7063.0833, 12414.0416, 15606.0208, 8518.5104, 8408.7552, 7319.8776]

# Check Reading and Prev Reading
print("EMA reading:", my_ema.reading())  # 7319.8776
print("Previouse EMA reading:", my_ema.prev_reading())  # 8408.7552

# How many EMA readings been generated
print(my_ema.reading_count()) # 9

# Purge Readings
my_ema.purge()
print("EMA reading after purging:", my_ema.reading())  # None
my_ema.recalculate()
print("EMA reading after recalculation:", my_ema.reading())  # 7319.8776

# Recalculate latest
my_ema.calculate_index("EMA_3")

# Access specific readings
print("Latest high reading:", my_ema.reading("high"))  # 4837
print("High reading at index -2:", my_ema.reading("high", index=-2))  # 6584

```

## Upcoming Features

Roughly ordered in priority

- More Indicators
- More Movement methods
- More Patterns
- Indicator Pluggability, to allow easy extension of this library
  - Allowing easier custom Indictors to be added
- Multiprocessing, of indictors stored within hexial Class.
  - Likely wont see increase in performance

## Testing

Testing is a critical aspect of this library due to the complexity of ensuring the accuracy of generated indicator values. To achieve this, I rely on [Pandas-TA](https://github.com/twopirllc/pandas-ta) as the source of truth for indicator values. Each indicator added to this library undergoes testing, where the output is compared against the corresponding indicator output from Pandas-TA. Due to slight differences in calculations, particularly within NumPy, not all values are exactly identical. Therefore, if differences exceed a given threshold (usually beyond one decimal place), a Pearson correlation coefficient is calculated to ensure correct correlation with the expected output.

### Speed Tests

The following charts illustrate the results and speed of Pandas-TA and Hexital in both bulk and incremental calculations. These results are obtained from running Pandas-TA and Hexital in bulk (_all candles calculated at once_) and incremental(_Caluclating after each new candle is added_) modes; chart _1_.

The incremental charts demonstrate the process of calculating technical analysis, adding one candle at a time, and recalculating up to a specified number of candles. It's evident that using Pandas-TA, Pandas, and NumPy for incremental data processing incurs significant performance overhead. This is primarily due to the underlying behavior of NumPy, which involves reallocating memory when appending or concatenating data, rather than resizing it. As a result, it's recommended in NumPy and Pandas documentation to gather all data prior to running calculations. On the other hand, Hexital, being purely Pythonic, exhibits efficient performance both in bulk and incremental processing, with minimal to no additional overhead time. It significantly outperforms Pandas-TA in incremental processing and even surpasses Pandas-TA in speed, especially with smaller datasets.

![EMA 10 test results.](tests/extra/speed_tests/EMA_10.png)

From chart _(2)_, it's evident that in bulk calculations with an extremely large dataset, Pandas-TA outperforms Hexital. Pandas-TA maintains consistent performance, with processing times starting at 0.08 seconds for 1,000 candles and remaining stable at this level for 10,000 candles. In contrast, Hexital exhibits faster processing times, starting at 0.025 seconds for 2,000 candles but increasing to 0.16 seconds for 10,000 candles. While Hexital is initially faster, there is a noticeable growth in processing time as the dataset size increases. Therefore, for backtesting with a large dataset, Pandas-TA offers superior performance, while Hexital may experience slowdowns.

![MACD 26 Bulk test results.](tests/extra/speed_tests/MACD_26_12_Bulk_Calculations.png)

However referencing chart _(3)_ being an example of using both these libraries for a live incremental application, whereby at n candles we incrementing a dataset with a candle and calculating the new TA; `Hexital` is far quicker. This is due to the speed that python can increment a list of data rather than Panda, as well as `Hexital` only needing to calculate the newest candle rather than having to re-calculate the entire dataset. Chart _3_ clearly shows the speed benefits it has over Pandas-TA and other Panda based Technical Analysis tools for incremental data sets.

![MACD 26 Real world usage.](tests/extra/speed_tests/MACD_26_12_real_world.png)

For reference, if using seconds Candle with 10,000 candles that is around 2 Hours 46 minutes.

#### Note

The code that produces these charts is: `tests/extra/speed_tests/run_speed_test.py` and can be ran by calling `make speed-test`. Some noise is seen due to running on personal laptop while in use.

## Inspiration

This library was inspired by [TALIpp](https://github.com/nardew/talipp), another Incremental Technical Analysis Library. However, I found the separate input lists rather cumbersome compared to working with an entire candle. Additionally, in TALIpp, outputs are separate entities, requiring extensive management. In contrast, Hexital stores all data within the candle, simplifying usage and management.
