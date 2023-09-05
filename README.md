# Hexital - Incremental Technical Analysis Library
[![license](https://img.shields.io/github/license/merlinr/hexital)](#license)
[![Python Version](https://img.shields.io/pypi/pyversions/hexital?style=flat)](https://pypi.org/project/hexital/)
[![PyPi Version](https://img.shields.io/pypi/v/hexital?style=flat)](https://pypi.org/project/hexital/)
[![Package Status](https://img.shields.io/pypi/status/hexital?style=flat)](https://pypi.org/project/hexital/)
[![Unit Tests - Master](https://github.com/MerlinR/Hexital/actions/workflows/unit_test.yaml/badge.svg?branch=master)](https://github.com/MerlinR/Hexital/actions/workflows/unit_test.yaml)
[![Unit Tests - Dev](https://github.com/MerlinR/Hexital/actions/workflows/unit_test.yaml/badge.svg?branch=development)](https://github.com/MerlinR/Hexital/actions/workflows/unit_test.yaml)

# `Alpha Development`❗
Note: Extremely early stages and likely change drastically, including core functionality and methods.
# Hexital
`Hexital` is a Python library implementing financial indicators for technical analysis. The distinctive feature of the library is its incremental computation of indicators which is designed to fit real-time applications or applications with iterative input in general.

For most libraries such as [Pandas-TA](https://github.com/twopirllc/pandas-ta) which is fantastic for generating Indicators for a large set of data, it's incredibly slow when computing real-time/incremental data sets. The entire input vector is always used to calculate new values of indicators, which is a major cause of this speed issue. Despite the fact that these indicator values will remain unchanged and/or you don't want past data points to be changed by new data. `Hexital` resolves this by using an incremental approach, only calculating new/missing indicator value's, this implies it requires O(1) time to produce new indicator values in comparison to O(n) (or worse) required by other libraries.


## Indicators
- ADX
- ATR
- KC
- EMA
- HighLowAverage
- MACD
- OBV
- RMA
- RSI
- ROC
- SMA
- STOCH
- Supertrend
- TR
- VWAP
- VWMA
- WMA


## Analysis
Simple useful Candle Anaylsis methods such as those in `Pine Scripting`
- Positive/Negative Candle
- Rising/Falling Indicator
- Mean Based Rising/Falling Indicator
- Highest/Lowest Indicator (Value)
- HighestBar/LowestBar Indicator (Offset how far back)
- Indicator Cross
- Indicator CrossOver/CrossUnder


## Indicators
Simple useful Candle pattern recognition, such as Doji, hammer, etc
- Badly Working Doji

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


## Upcoming Features

Roughly ordered in priority

- More Indicators
- More Analysis methods
- Pattern Candle recognition methods, detecting Doji, Hammer, etc
- Pattern Indicators, use above methods to run automatically as indicators
- Support for automatic multi timeframe indicator generation
  - E.G: With 1 minute candles, we can generate EMA for minute candles and 5 minute candles
- Indicator Pluggability, to allow easy extension of this library
  - Allowing custom Indictors to be added
- Multiprocessing, of indictors stored within hexial Class.
  - Likely wont see increase in performance


## Testing
Testing is a huge part of this library as it's incredibly difficult to ensure the accuracy of the indicator values being generated. In order to solve this this I rely on [Pandas-TA](https://github.com/twopirllc/pandas-ta) as my source of truth for the indicator values. Each indicator added to this library requires a test that uses the Pandas-TA lib indicator output as the expected result.

## Inspiration
This library was was inspired by [TALIpp](https://github.com/nardew/talipp) which is another Incremental Technical Analysis Library, however I disliked the seperate input lists rather then an entire candle, and futhermore outputs are seperated entities requiring lots of managing. Whereas Hexital stores all data within the Candles making easier usage.
