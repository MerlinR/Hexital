# Guide: Hexital strategies

!!! note "Advanced"
    You do not need this page for basic usage. Start with [Quick Start](quick-start.md) if you are new to Hexital.

[Hexital][hexital.core.hexital.Hexital] runs several indicators on one or more candle streams. Append a candle once; every indicator updates. Use it when a strategy needs shared candles, global settings, or multi-timeframe managers.

For a single indicator on a live feed, use `EMA(...).append()` directly — you do not need `Hexital`.

---

## Creating a strategy

=== "Indicator instances"

    ```python
    from hexital import EMA, SMA, Candle, Hexital

    strategy = Hexital("Demo", candles, [
        SMA(period=10),
        EMA(period=20),
    ])
    strategy.calculate()
    ```

=== "Dict config"

    Useful when loading from JSON or a database. Indicator class names must match exports in `hexital.indicators`.

    ```python
    strategy = Hexital("Demo", candles, [
        {"indicator": "SMA", "period": 10},
        {"indicator": "EMA", "period": 20},
    ])
    ```

=== "IndicatorCollection"

    When you want **typed, named access** to indicator objects — e.g. `strategy.collection.ema` — use [IndicatorCollection][hexital.core.indicator_collection.IndicatorCollection] with [HexitalCol][hexital.core.hexital.HexitalCol].

    Mark each indicator field with [indicator_field()][hexital.core.indicator_collection.indicator_field]:

    ```python
    from dataclasses import dataclass

    from hexital import EMA, HexitalCol, IndicatorCollection, SMA, indicator_field

    @dataclass
    class TrendStrategy(IndicatorCollection):
        ema: EMA = indicator_field(default_factory=EMA)
        sma: SMA = indicator_field(default_factory=lambda: SMA(period=20))

    strategy = HexitalCol("Trend", candles, TrendStrategy())
    strategy.calculate()

    strategy.collection.ema.reading()   # direct object access
    strategy.reading("EMA_10")          # strategy-level lookup still works
    ```

    Non-indicator fields (labels, config strings, etc.) are ignored unless marked with `indicator_field()`.

    For a simple explicit list without a dataclass:

    ```python
    ema = EMA()
    sma = SMA(period=20)
    collection = IndicatorCollection(ema, sma)
    strategy = Hexital("Trend", candles, collection)
    ```

---

## Reading values

Hexital is the **primary reading surface** for strategies. Pass an indicator name (or nested field) to the strategy — you do not need to reach through `strategy.indicators["EMA_10"]` for normal use.

```python
strategy.reading("EMA_10")              # latest value
strategy.prev_reading("EMA_10")         # previous bar
strategy.series("EMA_10")               # full series for one indicator
strategy.all_series()                   # dict of every top-level indicator
strategy.exists("EMA_10")               # True when latest reading is valid
```

Nested dict outputs use `:` between the indicator name and the field:

```python
strategy.reading("MACD_12_26_9:signal")
strategy.series("BBANDS_20:upper")
```

`strategy.indicator("EMA_10")` returns the underlying [Indicator][hexital.core.indicator.Indicator] object when you need direct access (custom logic, child inspection, etc.). For day-to-day strategy code, prefer `strategy.reading(...)`.

---

## Saving and restoring a strategy

Export the strategy configuration with [settings][hexital.core.hexital.Hexital.settings] and rebuild with [from_settings()][hexital.core.hexital.Hexital.from_settings]:

```python
import json

from hexital.utils.settings import decode_settings

saved = strategy.settings
# json.dumps handles your serialisation; decode timedelta fields after load
loaded = json.loads(json.dumps(saved, default=str))
restored = Hexital.from_settings(decode_settings(loaded), candles=candles)
restored.calculate()
```

Notes:

- Top-level indicator trees (e.g. DEMA's internal EMAs) rebuild in each indicator's `_initialise()` — you only serialise top-level entries.
- `source` round-trips as a string name (`"close"`, `"EMA_10"`, etc.).
- After loading, attach your candle history and call `calculate()` to repopulate readings.

---

## Candle streams

### `candles()`

Return the candle list for the default manager, a timeframe label, or an indicator name:

```python
strategy.candles()           # default stream
strategy.candles("T5")       # 5-minute manager
strategy.candles("EMA_10")   # stream where EMA_10 lives
```

### `candles_for()` and `candle_pair()`

Explicit helpers for which candle stream backs a reading:

```python
strategy.candles_for("EMA")              # single stream
strategy.candle_pair("EMA", "EMA_T5")    # two streams for cross-timeframe work
strategy.candle_pair("EMA", "high")      # indicator vs OHLCV on its stream
```

Movement analysis uses these internally when you pass a `Hexital` instance and two indicator names. See [Analysis](analysis-indepth.md#candle-streams-for-comparisons).

---

## Lifecycle

| Method | Purpose |
|--------|---------|
| `calculate()` | Run all top-level indicators over existing candles |
| `append()` / `prepend()` / `insert()` | Add candles; triggers incremental calculation |
| `add_indicator()` | Add indicators after construction (does not auto-calculate) |
| `remove_indicator()` | Detach and purge one top-level indicator |
| `purge()` | Clear readings from candles (recursive for nested children) |

---

## Global options

Settings on `Hexital` are broadcast to indicators where not overridden:

- `timeframe` / `timeframe_fill` — resampling transform
- `candle_life` — memory limit for long-running feeds
- `candlestick` — transform applied before indicators run (e.g. Heikin-Ashi)

See [Candles](candles.md#timeframes) and [Candlesticks](candlesticks.md).

---

## Further reading

- [Candles](candles.md) — readings on candles, export, `indicators` vs `sub_indicators`
- [Design](../about/design.md) — why readings live on candles and how sharing works
- [Analysis](analysis-indepth.md) — crossovers, rising/falling, multi-timeframe comparisons
