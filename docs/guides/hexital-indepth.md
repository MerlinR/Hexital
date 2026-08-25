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

## History and readiness

Use these when prefetching exchange history or validating a strategy before `calculate()`.

### `minimum_candles(timeframe=None)`

[Hexital.minimum_candles()][hexital.core.hexital.Hexital.minimum_candles] returns the **largest** `minimum_candles` among indicators on a candle series. Counts are in **that series' bar units**.

```python
strategy.minimum_candles()                    # all indicators
strategy.minimum_candles(timeframe="DEFAULT") # default stream only
strategy.minimum_candles(timeframe="T10")     # 10-minute indicators only
```

!!! warning "Multi-timeframe strategies"
    `minimum_candles()` without a `timeframe` takes the max across indicators, but each value may refer to a **different** bar size. For prefetch, pass the timeframe you are fetching — do not treat the unfiltered max as a single exchange request size.

### `has_sufficient_candles(timeframe=None)`

[Hexital.has_sufficient_candles()][hexital.core.hexital.Hexital.has_sufficient_candles] is `True` when every matching indicator's [is_ready][hexital.core.indicator.Indicator.is_ready] is `True` on its own stream:

```python
if strategy.has_sufficient_candles(timeframe="T10"):
    strategy.calculate()
```

### `minimum_candles_by_indicator(indicator=None)`

[Hexital.minimum_candles_by_indicator()][hexital.core.hexital.Hexital.minimum_candles_by_indicator] returns a name → count map for debugging prefetch:

```python
strategy.minimum_candles_by_indicator()
# {"EMA_10": 10, "RSI_14": 15}

strategy.minimum_candles_by_indicator(strategy.indicator("RSI_14"))
# {"RSI_14": 15}
```

### `minimum_candles_by_timeframe()`

[Hexital.minimum_candles_by_timeframe()][hexital.core.hexital.Hexital.minimum_candles_by_timeframe] returns the largest `minimum_candles` on each candle series — a prefetch plan when the strategy spans multiple timeframes:

```python
strategy.minimum_candles_by_timeframe()
# {"DEFAULT": 15, "T10": 10}
```

Keys match the labels passed to `minimum_candles(timeframe=...)` and `has_sufficient_candles(timeframe=...)`.

### Live-feed example

Hexital does not connect to an exchange — your feed fetches bars; Hexital validates and calculates:

```python
from hexital import EMA, RSI, Candle, Hexital

strategy = Hexital("live", [], [EMA(period=10), RSI(period=14)])

prefetch = strategy.minimum_candles_by_timeframe()  # {"DEFAULT": 15}
history = fetch_from_your_exchange(count=prefetch["DEFAULT"])

for candle in history:
    strategy.append(candle)

if strategy.has_sufficient_candles():
    strategy.calculate()
```

See [Quick Start — Live trading](quick-start.md#live-trading) for the full bootstrap loop.

Per-indicator details and custom overrides: [Indicators — History and readiness](indicators-indepth.md#history-and-readiness), [Custom indicators — Minimum candles](custom-indicator.md#minimum-candles).

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
