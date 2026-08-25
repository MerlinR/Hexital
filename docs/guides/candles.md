# Candles

!!! note "Reference"
    For your first indicator, you only need `Candle.from_dicts([...])`. See [Quick Start](quick-start.md). This page covers every way to create and configure candles.

Hexital uses its own [Candle][hexital.core.candle.Candle] type. Indicators read from a shared list of candles and store readings on each candle.

Required fields: `open`, `high`, `low`, `close`, `volume`.

Optional: `timestamp`, `timeframe` (bar-size label — see [Timeframes](#timeframes) below).

---

## Creating candles

=== "From dict (recommended)"

    ```python
    from hexital import Candle

    candle = Candle.from_dict({
        "open": 1.2345,
        "high": 1.2500,
        "low": 1.2300,
        "close": 1.2450,
        "volume": 10000,
    })

    candles = Candle.from_dicts([
        {"open": 1.0, "high": 1.2, "low": 0.9, "close": 1.1, "volume": 1000},
        {"open": 1.1, "high": 1.3, "low": 1.0, "close": 1.2, "volume": 1200},
    ])
    ```

=== "Directly"

    ```python
    from datetime import datetime
    from hexital import Candle

    candle = Candle(
        open=1.2345,
        high=1.2500,
        low=1.2300,
        close=1.2450,
        volume=10000,
        timestamp=datetime(2023, 12, 1, 14, 30),
    )
    ```

=== "From list"

    Order: `[timestamp (optional), open, high, low, close, volume, timeframe (optional)]`

    ```python
    from datetime import datetime
    from hexital import Candle

    candle = Candle.from_list(
        [datetime(2023, 12, 1, 14, 30), 1.2345, 1.2500, 1.2300, 1.2450, 10000]
    )
    ```

    Use [from_lists][hexital.core.candle.Candle.from_lists] for a list of lists.

=== "On append"

    Indicators accept dicts and lists directly — no need to wrap in `Candle` first:

    ```python
    from datetime import datetime
    from hexital import EMA

    ema = EMA(candles=[])
    ema.append([datetime(2023, 12, 1, 14, 30), 1.2345, 1.2500, 1.2300, 1.2450, 10000])
    ema.append({"open": 1.1, "high": 1.2, "low": 1.0, "close": 1.15, "volume": 500})
    ```

=== "From Pandas"

    ```python
    import pandas as pd
    from hexital import Candle, EMA

    df = pd.read_csv("path/to/symbol.csv")
    candles = Candle.from_dicts(df.to_dict("records"))

    ema = EMA(candles=candles)
    ema.calculate()
    ```

=== "From CSV"

    OHLCV-only CSV:

    ```python
    import pandas as pd
    from hexital import Candle

    df = pd.read_csv("ohlcv.csv", parse_dates=["timestamp"])
    candles = Candle.from_dicts(df.to_dict("records"))
    ```

    To persist **indicator readings** with candles, use JSON columns or a JSON file — see [Serialisation](../features.md#serialisation) and [Readings on candles](#readings-on-candles) below.

---

## Memory: `candle_life`

For long-running feeds, pass `candle_life` to drop candles older than a threshold:

```python
from datetime import timedelta
from hexital import EMA, Candle

ema = EMA(candles=candles, period=10, candle_life=timedelta(hours=2))
```

Culled candles take their indicator readings with them. Useful for memory limits; not needed for backtests on fixed datasets.

---

## Timeframes

Hexital separates **what your data is** from **what you transform it into**.

| | Where | Purpose |
|---|--------|---------|
| **Label** | `candle.timeframe` | Metadata: the native bar size of this OHLCV row (e.g. 1-minute). Set when you create or load candles. |
| **Transform** | `indicator.timeframe=` or `hexital.timeframe=` | Enables resampling in the manager (e.g. build 5-minute bars from 1-minute input). |

`candle.timeframe` does **not** turn on resampling, change indicator names, or configure managers. Only an explicit transform does.

### Resampling

Pass `timeframe=` on an indicator or [Hexital][hexital.core.hexital.Hexital] strategy to compress incoming candles (e.g. build 5-minute bars from 1-minute data). See [Features](../features.md) for multi-timeframe examples.

```python
from datetime import timedelta
from hexital import EMA, TimeFrame

ema = EMA(candles=[], timeframe=TimeFrame.MINUTE_5)
```

The indicator name picks up the transform suffix (e.g. `EMA_10_T5`). Indicators with no `timeframe=` keep an unqualified name regardless of candle labels.

### Label your input candles

Resampling managers only accept candles that carry a label **equal to or finer than** the manager transform. A 1-minute candle feeds a 5-minute EMA; a 5-minute candle does not feed a 1-minute passthrough manager's resample path.

```python
from datetime import timedelta
from hexital import EMA, Candle, TimeFrame

candles = Candle.from_dicts([
    {
        "open": 1.0, "high": 1.2, "low": 0.9, "close": 1.1, "volume": 1000,
        "timeframe": timedelta(minutes=1),  # or TimeFrame.MINUTE / "T1"
    },
])

ema = EMA(candles=[], timeframe=TimeFrame.MINUTE_5)
ema.append(candles[0])
```

**Passthrough managers** (no `timeframe=` on the indicator or strategy) accept any candle, labelled or not. Use these for raw 1:1 feeds.

**Unlabeled candles** are ignored by resampling managers — label at source (CSV column, exchange metadata, or when building `Candle` objects).

### Multi-timeframe strategies

[Hexital][hexital.core.hexital.Hexital] broadcasts each `append()` to every manager. Each manager applies its own filter and transform. You do not pass `timeframe=` to `append()` — routing is driven by candle labels and each manager's transform.

```python
from datetime import timedelta
from hexital import EMA, Hexital, Candle

strategy = Hexital("Demo", [], [EMA(), EMA(timeframe="T5")])

candle = Candle.from_dict({
    "open": 1.0, "high": 1.2, "low": 0.9, "close": 1.1, "volume": 1000,
    "timeframe": timedelta(minutes=1),
})
strategy.append(candle)  # passthrough manager + T5 resample manager
```

---

## Readings on candles

Each [Candle][hexital.core.candle.Candle] stores calculated values in two dicts:

| Dict | Contents |
|------|----------|
| `candle.indicators` | Top-level strategy indicators — what you added to `Hexital` or run standalone |
| `candle.sub_indicators` | Child and internal indicators — building blocks attached via `add_child()` |

When you export or persist candles, both dicts are included:

```python
candle.as_dict(readings=True)
# {"open": ..., "indicators": {"SMA_10": 1.23}, "sub_indicators": {"EMA_10": 1.21}, ...}
```

That split tells you **what is strategy-facing** vs **what is internal** without inferring from names alone.

Lookup helpers ([reading_by_candle][hexital.utils.candles.reading_by_candle], `strategy.reading()`) search both dicts transparently. Use the dict keys directly when serialising or inspecting raw candle data.

Export and reload:

```python
# Export
records = [c.as_dict(readings=True) for c in strategy.candles()]

# Reload
candles = Candle.from_dicts(records)
```

Full JSON/CSV/database examples: [Serialisation](../features.md#serialisation).

### Shared readings by name

Readings are keyed by **generated indicator name**, not by Python object identity. Two indicators with the same config write to the same slot — e.g. DEMA and TEMA both use `sub_indicators["EMA_10"]` when their child EMAs share settings.

| Benefit | Tradeoff |
|---------|----------|
| Same config → calculate once, reuse everywhere | `purge()` on one composite clears a slot another may share until recalc |
| Simple storage and export | Two separate child objects can share one candle slot |

This is intentional memoisation, not accidental collision. Identical generated names mean identical configuration.

A top-level `EMA(10)` writes to `indicators["EMA_10"]`. The same EMA as a child of DEMA writes to `sub_indicators["EMA_10"]` — same name, different buckets. Lookups check `indicators` first, then `sub_indicators`.

### Nested readings

Dict outputs (e.g. MACD, BBANDS) are read with `:` between the indicator name and the field:

```python
strategy.reading("MACD_12_26_9:signal")
strategy.reading("NATR:nested")  # if the dict key is "nested"
```

This matches [NESTED_DELI][hexital.core.constants.NESTED_DELI] (`:`). Generated indicator names never contain `:` — it is replaced with `-` in the name string itself.

See [Design](../about/design.md) for the full rationale.
