# Changelog

All notable changes to this project will be documented in this file.

The project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 0.1.2 - 2022-08-XX
- Added timestamp (datetime) to OHLCV dataclass
- More thorough unit testing
- Updated Indicators accuracy to Truth source
- Added private index property to Indicator allowing simplier method calls
  - self.reading_by_index(index, self.input_value) -> self.reading(self.input_value)
  - Multiple Method's renamed/argument re-ordered
## 0.1.1 - 2022-08-28
- Nada
## 0.1.0 - 2022-08-27

- Alpha release `hexital`