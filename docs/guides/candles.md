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

    [TODO](https://github.com/MerlinR/Hexital/issues/29)

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

Indicator values live on each candle under `candle.indicators`. Child and internal values use `candle.sub_indicators`. This makes candles serialisable and lets you resume incremental calculation after a restart.

### Nested readings

Dict outputs (e.g. MACD, BBANDS) are read with `:` between the indicator name and the field:

```python
strategy.reading("MACD_12_26_9:signal")
strategy.reading("NATR:nested")  # if the dict key is "nested"
```

This matches [NESTED_DELI][hexital.core.constants.NESTED_DELI] (`:`). Generated indicator names never contain `:` — it is replaced with `-` in the name string itself.

See [Design](../about/design.md) for the rationale.
