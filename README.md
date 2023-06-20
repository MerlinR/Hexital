# Hexital - Incremental Technical Analysis Library

`Hexital` is a Python library implementing financial indicators for technical analysis. The distinctive feature of the library is its incremental computation of said indicators which fits extremely well real-time applications or applications with iterative input in general.

## Upcoming Features

Roughly ordered in priority

- More Indicators
- More Utilities
- Pattern Candle methods, detecting Doji, Hammer, etc
- Pattern Indicators, use above methods to run automatically as indicators
- Possible support for automatic multi timeframe indicator generation
  - E.G: With 1 minute candles, we can generate EMA for minute candles and 5 minute candles
- Indicator Pluggability, to allow easy extension of this library
- Multiprocessing, of indictors stored within hexial Class.

### Alternatives

This library is not unique, there are many libraries avaiable for generating TA, and many with more Indicator options.
[TALIpp(https://github.com/nardew/talipp) is inspirition for this library, by also being an Incremental Technical Analysis Library, however I disliked the way inputs are seperate lists from the candles, and that outputs are seperate from the data.