# Guide: History and readiness

!!! note "Who this is for"
    Use this guide when you **prefetch exchange history**, **bootstrap a live feed**, or need to know **how many candles to load** before indicators produce valid readings. Hexital advises bar counts — it does **not** fetch candles for you.

---

## The problem

Indicators need warm-up bars before their formulas are defined. If you call `calculate()` on five candles but RSI needs fifteen, early bars stay `None` and your strategy may act on missing data.

Hexital exposes **readiness** separately from **calculation**:

| Question | API | Answers |
|----------|-----|---------|
| How many bars does this indicator need? | `minimum_candles` | A 1-based bar count |
| Have I loaded enough bars yet? | `is_ready` / `has_sufficient_candles()` | Compares loaded history to `minimum_candles` |
| Does this indicator have a value on the latest bar? | `exists()` / `reading()` | Whether `calculate()` produced a non-`None` reading |

!!! important "Ready ≠ calculated"
    `is_ready` only checks **bar count** on the indicator's own candle stream. It does not run `calculate()` or guarantee a non-`None` reading. After history is loaded, call `calculate()` once, then use `exists()` or `reading()` before trading logic.

---

## Counting: 1-based bar units

[Indicator.minimum_candles][hexital.core.indicator.Indicator.minimum_candles] is **1-based**:

- `10` → the **10th candle** is the first that *may* have a reading after `calculate()`
- `15` for `RSI(period=14)` → needs `period + 1` bars (prior bar for direction)

```python
from hexital import EMA, RSI

EMA(period=10).minimum_candles   # 10
RSI(period=14).minimum_candles   # 15
```

Counts are always in **that indicator's bar units** — default-stream bars for a plain EMA, resampled 5-minute bars for `EMA(timeframe="T5")`, etc.

---

## Single indicator

### `minimum_candles`

Property on [Indicator][hexital.core.indicator.Indicator]. Defaults to `period` when the indicator has a `period` field. Composites take the **maximum** of their own override and every child's `minimum_candles` (e.g. MACD, BBANDS).

| Value | Meaning |
|-------|---------|
| `period` | Default for SMA-style indicators |
| Custom | Override `_minimum_candles()` when warm-up differs (RSI, ADX, etc.) |
| `0` | Unknown — no `period` and no override ([Amorph][hexital.indicators.amorph.Amorph] without prefetch hints) |

### `is_ready`

[Indicator.is_ready][hexital.core.indicator.Indicator.is_ready] is `True` when `len(candles) >= minimum_candles` on **that indicator's stream**. When `minimum_candles` is `0`, any loaded candle counts as ready.

```python
ema = EMA(period=10, candles=history)
if ema.is_ready:
    ema.calculate()
if ema.exists():
    print(ema.reading())
```

### Child breakdown

[Indicator.minimum_candles_by_indicator()][hexital.core.indicator.Indicator.minimum_candles_by_indicator] lists each **child** name → count — useful when debugging composites:

```python
macd = MACD(candles=candles)
macd.minimum_candles_by_indicator()
# {"MACD_12_26_9_fast": 12, "MACD_12_26_9_slow": 26, ...}
```

Custom overrides: [Custom indicators — Minimum candles](custom-indicator.md#minimum-candles).

---

## Hexital strategy

Strategy-level helpers aggregate across **registered top-level indicators**. Each indicator is checked on **its own candle manager**, not on the strategy's primary `candles()` length alone.

### `minimum_candles(timeframe=None)`

[Hexital.minimum_candles()][hexital.core.hexital.Hexital.minimum_candles] returns the **largest** `minimum_candles` among matching indicators:

```python
strategy.minimum_candles()                    # all indicators (see warning below)
strategy.minimum_candles(timeframe="DEFAULT") # default stream only
strategy.minimum_candles(timeframe="T10")     # 10-minute indicators only
```

### `has_sufficient_candles(timeframe=None)`

[Hexital.has_sufficient_candles()][hexital.core.hexital.Hexital.has_sufficient_candles] is `True` when **every** matching indicator's `is_ready` is `True`:

```python
if strategy.has_sufficient_candles(timeframe="T10"):
    strategy.calculate()
```

### `minimum_candles_by_indicator(indicator=None)`

[Hexital.minimum_candles_by_indicator()][hexital.core.hexital.Hexital.minimum_candles_by_indicator] — name → count for debugging:

```python
strategy.minimum_candles_by_indicator()
# {"EMA_10": 10, "RSI_14": 15}

strategy.minimum_candles_by_indicator(strategy.indicator("RSI_14"))
# {"RSI_14": 15}
```

### `minimum_candles_by_timeframe()`

[Hexital.minimum_candles_by_timeframe()][hexital.core.hexital.Hexital.minimum_candles_by_timeframe] — **prefetch plan** when the strategy spans multiple series:

```python
strategy.minimum_candles_by_timeframe()
# {"DEFAULT": 15, "T10": 10}
```

Keys match the labels passed to `minimum_candles(timeframe=...)` and `has_sufficient_candles(timeframe=...)`. The default stream uses `"DEFAULT"` (indicators with no `timeframe=` transform).

!!! warning "Multi-timeframe prefetch"
    `minimum_candles()` **without** a `timeframe` takes the max across indicators, but each value may refer to a **different bar size**. Do not treat that single number as one exchange request. Use `minimum_candles_by_timeframe()` and fetch **each series separately**.

---

## Live bootstrap workflow

Hexital does not connect to an exchange. Your feed fetches OHLCV; Hexital validates and calculates.

```python
from hexital import Candle, EMA, Hexital, RSI

strategy = Hexital("live", [], [EMA(period=10), RSI(period=14)])

# 1. Prefetch plan — your code fetches from the exchange
prefetch = strategy.minimum_candles_by_timeframe()
# {"DEFAULT": 15}

history = fetch_bars(count=prefetch["DEFAULT"])  # not Hexital

# 2. Load history
for candle in history:
    strategy.append(candle)

# 3. Readiness, then first full calculation
if strategy.has_sufficient_candles():
    strategy.calculate()

# 4. Live loop — append triggers incremental recalc
while True:
    candle = await next_bar()
    strategy.append(candle)
    if strategy.exists("RSI_14"):
        ...
```

| Step | Your layer | Hexital |
|------|------------|---------|
| How many bars to fetch? | Read `minimum_candles_by_timeframe()` | Per-series bar counts |
| Enough loaded? | `has_sufficient_candles()` | Each indicator on its own stream |
| First full calc | `calculate()` after history | Fills missing readings |
| Each new bar | `append(candle)` | Incremental update |

See also [Quick Start — Live trading](quick-start.md#live-trading).

### Multi-timeframe example

```python
from datetime import timedelta
from hexital import EMA, Hexital, Candle

strategy = Hexital("mtf", [], [
    EMA(period=10),                    # default stream
    EMA(period=10, timeframe="T5"),    # 5-minute stream
])

prefetch = strategy.minimum_candles_by_timeframe()
# {"DEFAULT": 10, "T5": 10}

history_1m = fetch_bars(count=prefetch["DEFAULT"], interval="1m")
for c in history_1m:
    c.timeframe = timedelta(minutes=1)
    strategy.append(c)

# Readiness per series
assert strategy.has_sufficient_candles(timeframe="DEFAULT")
assert strategy.has_sufficient_candles(timeframe="T5")

strategy.calculate()
```

Resampled managers build coarser bars from finer labelled input — you still **append** the finest feed you have; see [Candles — Timeframes](candles.md#timeframes).

---

## Amorph and analysis lookback

### Amorph prefetch hints

[Amorph][hexital.indicators.amorph.Amorph] resolves `minimum_candles` from kwargs (stripped before the analysis call):

| Kwarg | Used for |
|-------|----------|
| `minimum_candles` | Explicit prefetch count |
| `period` | When the wrapped function accepts `period` |
| `lookback` | Window size; with `period`, combined as `period + lookback - 1` |

```python
from hexital import Amorph
from hexital.analysis.patterns import doji

Amorph(analysis=doji, minimum_candles=11)
Amorph(analysis=doji, lookback=20, minimum_candles=30)
```

Without hints, Amorph reports `minimum_candles == 0` — prefetch is your responsibility.

### Analysis functions vs indicator warm-up

[Analysis helpers](analysis-indepth.md) (`crossover`, `highest`, patterns, etc.) have their own **lookback windows** at call time. That is separate from indicator `minimum_candles`. A pattern with `lookback=20` may need 20 bars of **calculated** readings even when the wrapped indicator's `minimum_candles` is lower — plan prefetch for both.

---

## Common mistakes

| Mistake | Fix |
|---------|-----|
| Using `len(strategy.candles())` for readiness | Use `has_sufficient_candles()` — each indicator checks its own manager |
| One fetch size for multi-timeframe strategies | Use `minimum_candles_by_timeframe()` — separate counts per series |
| Assuming `is_ready` means RSI has a value | Call `calculate()`, then `exists()` / `reading()` |
| Treating unfiltered `minimum_candles()` as one API call | Pass `timeframe=` or use `minimum_candles_by_timeframe()` |
| Expecting Hexital to fetch history | Your exchange/DB layer fetches; Hexital only advises counts |

---

## Quick reference

| Scope | How many bars? | Enough loaded? | Has a reading? |
|-------|----------------|----------------|----------------|
| Indicator | `.minimum_candles` | `.is_ready` | `.exists()` / `.reading()` |
| Hexital | `.minimum_candles(tf=…)` | `.has_sufficient_candles(tf=…)` | `.exists(name)` / `.reading(name)` |
| Prefetch plan | `.minimum_candles_by_timeframe()` | per-key `has_sufficient_candles(tf=…)` | after `calculate()` |

---

## Further reading

- [Strategies (Hexital)](hexital-indepth.md) — managers, settings, multi-timeframe setup
- [Candles](candles.md) — creating candles, timeframe labels, readings on candles
- [Custom indicators](custom-indicator.md) — `_minimum_candles()` overrides
- [Indicators (advanced)](indicators-indepth.md) — incremental calculation details
