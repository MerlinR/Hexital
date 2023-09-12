# Changelog

All notable changes to this project will be documented in this file.

The project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
## 0.2.1
- Added Patterns:
  - Doji Candle
- Added append method to Indicator just like Hexital
- Fixed bug where Hexital would alter indicator list
- Fixed bug in _find_calc_index with no candles
- Added Pattern Indicator, skeleton to run Any Patterns as a Indicator
  - E.G On all Candles automatically

## 0.2.0 - 2023-09-05
- Feature: Added timestamp (datetime) to Candle dataclass
- Feature: Can convert Candle from list and dict
- Feature: Can set timestamp(datetime) in lists/dict Candle conversion
- Feature: Added _validate_fields method to Indicators
- Added custom exceptions
- More thorough unit testing
- Updated Indicators accuracy to Truth source
- Added private index property to Indicator allowing simplier method calls
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