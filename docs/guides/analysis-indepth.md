# Guide: Analysis

!!! note "Advanced"
    You do not need this page for basic usage. Start with [Quick Start](quick-start.md) if you are new to Hexital.

Hexital's [analysis][hexital.analysis] module provides Pine Script–style helpers: crossovers, rising/falling checks, highest/lowest over a window, and more. Full catalogue: [analysis catalogue](../analysis-catalogue.md).

Analysis functions accept three kinds of data source:

| Source | When to use |
|--------|-------------|
| `list[Candle]` | You already have candles with readings attached |
| `Indicator` | One indicator's candle stream |
| `Hexital` | Strategy with named indicators — pass indicator names as strings |

---

## Basic usage

```python
from hexital import EMA, WMA, Hexital
from hexital.analysis import cross, rising

strategy = Hexital("Demo", candles, [EMA(period=3), WMA(name="WMA", period=8)])
strategy.calculate()

rising(strategy, "EMA_3", length=8)       # True if EMA rose over last 8 bars
cross(strategy, "EMA_3", "WMA")           # True if EMA crossed WMA recently
```

With a single indicator:

```python
ema = EMA(candles=candles, period=10)
ema.calculate()

rising(ema, "EMA_10", length=5)
```

With raw candles (readings must already be on the candles):

```python
from hexital.analysis import above

above(candles, "EMA_10", "SMA_20")
```

---

## Candle streams for comparisons

When comparing two series on a [Hexital][hexital.core.hexital.Hexital] strategy, movement functions need to know which candle stream each name lives on.

**Same stream** — both indicators on one manager (e.g. EMA vs SMA on 1-minute data):

```python
from hexital.analysis import above

above(strategy, "EMA_10", "SMA_20")   # one stream, both names
```

**Different timeframes** — pass both names; Hexital resolves streams via [candle_pair()][hexital.core.hexital.Hexital.candle_pair] and aligns bars by timestamp:

```python
strategy = Hexital("MTF", candles, [
    EMA(name="EMA"),
    EMA(name="EMA_T5", timeframe="T5"),
])
strategy.calculate()

above(strategy, "EMA", "EMA_T5")
```

**Indicator vs OHLCV** — compare an indicator to `high`, `low`, `close`, etc. on the indicator's stream:

```python
above(strategy, "EMA_10", "high")
```

You can also resolve streams explicitly:

```python
stream = strategy.candles_for("EMA_10")
pair = strategy.candle_pair("EMA", "EMA_T5")   # (ema_candles, ema_t5_candles)
```

Movement functions that take two indicator names (`above`, `below`, `cross`, `crossover`, `crossunder`, etc.) use this resolution automatically when the first argument is a `Hexital` instance.

To cross a **fixed threshold** (e.g. RSI through 30), use [crossover_level()][hexital.analysis.movement.crossover_level] or [crossunder_level()][hexital.analysis.movement.crossunder_level]:

```python
from hexital.analysis import crossover_level, crossunder_level, between

crossover_level(strategy, "RSI_14", 30)   # prev <= 30 and current > 30
crossunder_level(strategy, "RSI_14", 70)  # prev >= 70 and current < 70
between(strategy, "RSI_14", 30, 70)
```

Inside a signal indicator's `_calculate_reading()`, use the scalar helpers from [hexital.analysis.signals][hexital.analysis.signals] (`crossed_above(rsi, prev_rsi, 30)`, etc.).

Single-series functions (`rising`, `bars_since`, `highest`, etc.) take one indicator name and use [candles_for()][hexital.core.hexital.Hexital.candles_for] when given a `Hexital` instance.

For reusable entry/exit rules as incremental indicators, see [Custom indicators — Signal indicator](custom-indicator.md#recipe-d--signal-indicator) and [hexital.analysis.signals][hexital.analysis.signals].

---

## Patterns and Amorph

Pattern functions live in [hexital.analysis.patterns][hexital.analysis.patterns]. They operate on candle sequences directly.

For one-off logic that should run on every append, use [Amorph][hexital.indicators.amorph.Amorph] — a top-level indicator that wraps a callable. See [Custom indicators](custom-indicator.md#amorph).

---

## Further reading

- [Analysis catalogue](../analysis-catalogue.md) — every function and signature
- [Hexital strategies](hexital-indepth.md) — `candles_for`, `candle_pair`, multi-timeframe setup
- [Candles](candles.md) — timeframe labels and resampling
