# Changelog

All notable changes to this project will be documented in this file.

The project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
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