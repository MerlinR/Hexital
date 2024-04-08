# Changelog

All notable changes to this project will be documented in this file.

The project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 1.0.1 - 2024-04-08
- Fixed #12 Inaccurate verify_indicators method in Hexital

## 1.0.0 - 2024-02-11
- Moving Into BETA
- Added CandleManager
  - CandleManger replaces List[Candle] to manage Candles and controls CandlestickTypes, timeframes and lifespan
- Added CandlestickType
  - CandlestickType modular parent to convert candlesticks to alt types,
  - E.G Auto convert candles to heikin-ashi
  - Can be added as str 'candlestick_type="ha"' for heikin-ashi
- Converted Candle to Class from Dataclass
- Added Many Candle analysis methods to Candle:
  - Positive, Negative, realbody, shadow_upper, shadow_lower, high_low
- Added Tag and 'clean_values' to Candle to support conversion of Candlesticks
- Added Pattern_map, Movement_map, Indicator_map and Candlestick_map for easier control and possible modular altering
- Added Heikin-Ashi candlestick conversion
- Added better config inheritance from Hexital to Indicators
- Added calculate_index to hexital
- Added ability to call the movement and pattern methods from Hexital and Indicator for easier usage
  - above, below, cross, crossover, doji, hammer, etc..
- Added sanitise_name to convert '.' to ',' to support name nesting
- Added more Exceptions to improve error's
- Added Candle ability to accept json str timestamp, therefore allowing direct conversion from Pandas -> Hexital
- Fixed Hammer index pattern working correctly
- Changed Sub/managed indicators to auto populate candles field
- Changed 'as_list' property a method that can now take a nested indicator name
- Removed read property
- Renamed utils/candlesticks to utils/candles

## 0.4.0 - 2024-01-22
- Cleaned up code and some potential Bugs ruff/pyright
- Added movement Above/Below and updated others to use it
- Updated collapse candle 'fill' to show essentially doji candle rather than copy prev
- Added Patterns:
  - Hammer Candle
- Added a TimeFrame Enum with common timeframes for easier usage
- Renamed Pattern to Amorph and updated to only require either 'indicator' or 'analysis'
- Renamed candles_timerange to candles_lifespan, to be clearer of purpose and avoid confusion with candles_timeframe
- Updated Hexital/Amorph to accept patterns, movements and custom methods
- Major Fix: Re-wrote collapse_candles_timeframe to correctly handle candles,gaps and appending
- Fixed Doji pattern
- Fixed Supertrend Indicator
- Fixed Timeframe bug with candles reference in indicator that use sub indicators
- Fixed possible error in VWAP with no volumes traded
- Fixed bug with nested Indicator returning None for valid 0 Value
- Fixed purge not correctly purge sub and managed indicators

## 0.3.1 - 2023-10-09
- Added candles_timerange to auto remove older than N candles
- Added 'Settings' propety, to output Indicator in a dict format, that can be fed into back into Hexital
- Updated Hexital to better take Pattern's as a dict input
- Updated Hexital dict input to accept custom method Patterns
- Fixed bug in Movement on to few candles
- Fixed bug where no timeframe indicator wasnt creating new copy of candles
- Fixed bug where collapsed timeframe candles will use first calculated indicator value
  - Meaning 1 minute candle that only had first 10 seconds,  will never re-calculate for rest of the minute

## 0.3.0 - 2023-09-27
- Added Patterns:
  - Doji Candle
- Added append method to Indicator just like Hexital
- Fixed bug where Hexital would alter indicator list
- Fixed bug in _find_calc_index with no candles
- Added Pattern Indicator, skeleton to run Any Patterns as a Indicator
  - E.G On all Candles automatically
- Added support to generate Indicators on multiple timeframes at once
  - Allowing one set of candles to be used to generate higher timeframe indicators
  - E.G 1m candles can be used to generate 10m indicators simultaneously with 1m indicators

## 0.2.0 - 2023-09-05
- Feature: Added timestamp (datetime) to Candle dataclass
- Feature: Can convert Candle from list and dict
- Feature: Can set timestamp(datetime) in lists/dict Candle conversion
- Feature: Added _validate_fields method to Indicators
- Added custom exceptions
- More thorough unit testing
- Updated Indicators accuracy to Truth source
- Added private index property to Indicator allowing simpler method calls
  - self.reading_by_index(index, self.input_value) -> self.reading(self.input_value)
  - Multiple Method's renamed/argument re-ordered
- Added Indicators:
  - ADX
  - HighLowAverage
  - KC
  - OBV
  - RMA
  - ROC
  - STOCH
  - SuperTrend
  - VWAP
  - VMA
  - WMA
  
## 0.1.1 - 2023-08-28
- Nada

## 0.1.0 - 2023-08-27
- Alpha release `hexital`
