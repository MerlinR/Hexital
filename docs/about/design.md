# Design And Future Plans

## Design

Hexital is designed with usability and ease of use in mind, making it simple to add new candles and automatically generate indicators while identifying patterns or trends. Inspired by [Pandas-TA](https://github.com/twopirllc/pandas-ta), Hexital allows you to create an object configured with indicators across multiple timeframes. By appending a new candle, all updated indicator values are ready for immediate use in your trading strategy.

A unique aspect of Hexital is that results are stored directly within the candles, rather than within indicator objects. This design ensures that even if you clear your Hexital instance or indicators, the candles retain their indicator readings. This makes it easy to export and save candles to a database for reuse elsewhere.

Additionally, this approach supports caching candles. If the application is restarted, the cached candles, combined with the Hexital configuration, can seamlessly restore both the candles and their indicator values, enabling incremental calculations to resume immediately.




## Future Plans

Hexital is currently in `Beta`. The focus during this phase is to avoid altering core frameworks and instead prioritise making the library more robust and user-friendly. The current implementation of indicators and patterns is straightforward, allowing for easy expansion. However, the addition of new indicators will slow down temporarily to concentrate on enhancing robustness, ease of use, standardization, and error handling.

### Plans
An outline of planned goals for Hexital, in no particular order:

- Robust code
    - Better Error handling
    - Clearer methods to expected outputs
    - Full docstrings
- More Quality of life features
- 100% Test coverage
- More Indicators
- More Movement methods
- More Patterns
- Indicator Pluggability, allow easy way to easily extend Hexital Indictors with own created indicators
    - Allowing easier custom Indicators to be added
- Multiprocessing, of indicators stored within hexital Class.
    - Likely wont see increase in performance

---

## Inspiration

Hexital was inspired by [Pandas-TA](https://github.com/twopirllc/pandas-ta) and [TALIpp](https://github.com/nardew/talipp), another Incremental Technical Analysis Library. However, I found Tallip usage with separate input lists rather cumbersome compared to working with an entire candle. Additionally, in TALIpp, outputs are separate entities, requiring extensive management. In contrast, Pandas-TA was easy to work with, and offered a way to use one set of input data and have multiple Indicator's for a Candle and results existing within one Candle; however was slower for incremental data due to Panda's.

Hexital took the inspiration from Tallip incremental calculation, and Pandas-TA ease of use and grouped Indicators and easy to read results. It was further extended from Pandas-TA by offering methods to detect candlestick patterns; however goes further offering analysis tools and the ability to compress data into different timeframes.