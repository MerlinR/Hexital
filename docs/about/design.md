# Design And Future Plans

## Design

Hexital is designed with usability and ease of use in mind, making it simple to add new candles and automatically generate indicators while identifying patterns or trends. Inspired by [Pandas-TA](https://github.com/twopirllc/pandas-ta), Hexital allows you to create an object configured with indicators across multiple timeframes. By appending a new candle, all updated indicator values are ready for immediate use in your trading strategy.

### Readings live on candles

A unique aspect of Hexital is that results are stored directly within the candles, rather than only inside indicator objects. This design ensures that even if you clear your Hexital instance or indicators, the candles retain their indicator readings. This makes it easy to export and save candles to a database for reuse elsewhere.

Additionally, this approach supports caching candles. If the application is restarted, the cached candles, combined with the Hexital configuration, can seamlessly restore both the candles and their indicator values, enabling incremental calculations to resume immediately.

Each candle holds two reading dicts:

- **`indicators`** — top-level strategy outputs (what you registered on `Hexital`)
- **`sub_indicators`** — child and internal values (composite building blocks)

When you export candles, that split is preserved so consumers can tell strategy-facing readings from internals. See [Candles](../guides/candles.md#readings-on-candles).

### Shared storage by name

Readings are keyed by generated indicator name. Identical configuration produces the same name and therefore the same candle slot — so DEMA and TEMA can share an `EMA_10` child without a central registry. This is deliberate memoisation: same settings should yield the same result in one place.

Purging or removing one composite may clear a slot another indicator still references until the next `calculate()`. That tradeoff keeps storage and sharing simple.

### Hexital as the strategy facade

[Hexital][hexital.core.hexital.Hexital] orchestrates candles, managers, and top-level indicators. **`strategy.reading("EMA_10")`** is the intended way to query a strategy — one entry point for names, nested fields, and multi-timeframe lookup.

Indicator objects remain available (`strategy.indicator("EMA_10")`, `HexitalCol.collection.ema`) for authors who need direct access. The strategy-level reading API is not a thin wrapper to remove; it is how most strategy code should read values.

### Timeframe labels vs transforms

`candle.timeframe` is stored on each bar as metadata (what resolution the row represents). Resampling is configured separately via `indicator.timeframe=` or `hexital.timeframe=`. Managers route appended candles by label: a resampling manager accepts bars labelled at its transform size or finer. See [Candles](../guides/candles.md#timeframes) for usage.

Indicator names are generated from `_name_parts()` on each indicator class.

### Explicit over implicit

Recent API choices favour clear contracts over runtime guessing:

- **`indicator_field()`** — marks which `IndicatorCollection` fields belong to the strategy
- **`candles_for()` / `candle_pair()`** — explicit candle streams for movement analysis
- **`from_settings()`** — documented path to rebuild a strategy from saved config

Dict-based indicator construction (`{"indicator": "SMA", "period": 10}`) is intentional for JSON persistence. See [Hexital strategies](../guides/hexital-indepth.md#saving-and-restoring-a-strategy).


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