# Hexital - Incremental Technical Analysis Library

[![Python Version](https://img.shields.io/pypi/pyversions/hexital?style=flat)]()
[![PyPi Version](https://img.shields.io/pypi/v/hexital?style=flat)](https://pypi.org/project/hexital/)
[![Package Status](https://img.shields.io/pypi/status/hexital?style=flat)](https://pypi.org/project/hexital/)
![GitHub Release Date](https://img.shields.io/github/release-date/merlinr/hexital?color=pink)
[![Downloads](https://static.pepy.tech/badge/hexital)](https://pepy.tech/project/hexital)
[![Downloads](https://static.pepy.tech/badge/hexital/month)](https://pepy.tech/project/hexital)
![GitHub Repo stars](https://img.shields.io/github/stars/MerlinR/Hexital?style=flat)
[![Unit Tests - Master](https://github.com/MerlinR/Hexital/actions/workflows/unit_test.yaml/badge.svg?branch=master)](https://github.com/MerlinR/Hexital/actions/workflows/unit_test.yaml)
[![Unit Tests - Dev](https://github.com/MerlinR/Hexital/actions/workflows/unit_test.yaml/badge.svg?branch=development)](https://github.com/MerlinR/Hexital/actions/workflows/unit_test.yaml)
[![license](https://img.shields.io/github/license/merlinr/hexital)]()

**Source Code**: [https://github.com/MerlinR/Hexital](https://github.com/MerlinR/Hexital)

---

Hexital is a fast, zero-dependency Python library for technical analysis. It computes indicators **incrementally** — append a candle, get the new reading — instead of recalculating the entire series each time.

* **Fast** — built for live feeds and append-one-candle workflows
* **Easy** — dicts, lists, or `Candle` objects as input
* **Versatile** — indicators, patterns, candlestick transforms, analysis helpers
* **Lightweight** — no pandas or numpy required at runtime

> **Beta:** Breaking changes are still possible. See the [Release Notes](changelog.md).

---

## Installation

```bash
pip install hexital
```

Development branch:

```bash
pip install git+https://github.com/merlinr/hexital.git@development
```

---

## Choose your path

| I want to… | Use | Guide |
|------------|-----|-------|
| Compute one indicator on a live feed | `EMA(...).append()` | [Quick Start](guides/quick-start.md) |
| Run several indicators on one candle stream | `Hexital(...)` | [Strategies](guides/hexital-indepth.md) |
| Load candles from CSV, Pandas, timestamps | `Candle.from_dicts()` etc. | [Candles](guides/candles.md) |
| Build 5m bars from 1m data | `timeframe=` on indicator + label on candles | [Candles](guides/candles.md) · [Features](features.md) |
| Check crossovers, rising/falling | `hexital.analysis` | [Analysis](guides/analysis-indepth.md) |
| Heikin-Ashi or other candle transforms | `candlestick=` | [Candlesticks](guides/candlesticks.md) |
| Write my own indicator | subclass `Indicator` | [Custom indicators](guides/custom-indicator.md) |
| Browse what's built in | catalogues | [Indicators](indicator-catalogue.md) · [Patterns](candle-pattern-catalogue.md) |

**New here?** [Quick Start](guides/quick-start.md) walks through the examples below step by step.

---

## Getting started

### Single indicator

```python
from hexital import EMA, Candle

candles = Candle.from_dicts([
    {"open": 17213, "high": 2395, "low": 7813, "close": 3615, "volume": 19661},
    {"open": 1301, "high": 3007, "low": 11626, "close": 19048, "volume": 28909},
])

ema = EMA(candles=candles, period=3)
ema.calculate()
print(ema.reading())  # 8408.7552

# Append updates the reading automatically
ema.append(Candle.from_dict({"open": 19723, "high": 4837, "low": 11631, "close": 6231, "volume": 38993}))
print(ema.reading())  # 7319.8776
```

### Hexital — multiple indicators, one candle stream

Use [Hexital][hexital.core.hexital.Hexital] when a strategy needs several indicators fed from the same candles:

```python
from hexital import EMA, WMA, Candle, Hexital

candles = Candle.from_dicts([
    {"open": 17213, "high": 2395, "low": 7813, "close": 3615, "volume": 19661},
    {"open": 1301, "high": 3007, "low": 11626, "close": 19048, "volume": 28909},
    {"open": 12615, "high": 923, "low": 7318, "close": 1351, "volume": 33765},
])

strategy = Hexital("Demo Strat", candles, [
    WMA(name="WMA", period=8),
    EMA(period=3),
])
strategy.calculate()

print(strategy.reading("EMA_3"))  # 8408.7552
print(strategy.reading("WMA"))    # 9316.4722

strategy.append(Candle.from_dict({"open": 19723, "high": 4837, "low": 11631, "close": 6231, "volume": 38993}))
print(strategy.reading("EMA_3"))  # 7319.8776
print(strategy.reading("WMA"))    # 8934.9722
```

Named indicators keep stable keys (`WMA`). Unnamed indicators get generated names from type and settings (`EMA_3` = EMA with period 3).

---

## What's included

### Indicators

40+ incremental indicators for common strategies. Full reference: [indicator catalogue](indicator-catalogue.md).

`ADX` · `Amorph` · `AROON` · `ATR` · `BBANDS` · `CCI` · `CMO` · `Counter` · `Donchian` · `EMA` · `HL` / `HLA` / `HLCA` · `HMA` · `Ichimoku` · `JMA` · `KC` · `MACD` · `MFI` · `MOP` · `OBV` · `PPO` · `PSAR` · `PivotPoints` · `RMA` · `ROC` · `RSI` · `RVI` · `SMA` · `Squeeze` / `SqueezePro` · `STDEV` / `STDEVT` · `STOCH` · `Supertrend` · `TR` · `TSI` · `VWAP` · `VWMA` · `WillR` · `WMA` · `ZScore`

### Candlestick patterns

Pattern detection on candle sequences — [full catalogue](candle-pattern-catalogue.md).

`doji` · `dojistar` · `hammer` · `inverted_hammer`

### Candlestick types

Transform incoming candles before indicators run (e.g. Heikin-Ashi) — [catalogue](candlesticks-catalogue.md).

`HeikinAshi`

### Movements

Pine Script–style helpers for indicator behaviour over time — [full catalogue](analysis-catalogue.md).

`positive` / `negative` · `rising` / `falling` · `mean_rising` / `mean_falling` · `highest` / `lowest` · `highestbar` / `lowestbar` · `cross` / `crossover` / `crossunder` · `value_range`

```python
from hexital.analysis import cross, rising

rising(ema, "EMA_3", length=8)
cross(strategy, "EMA_3", "WMA")
```

---

## Testing & performance

### Accuracy

Every built-in indicator is unit tested against [Pandas-TA](https://github.com/twopirllc/pandas-ta) as a source of truth. Values are compared with a small tolerance where floating-point or formula differences apply.

### When to use Hexital vs Pandas-TA

| Use case | Better fit |
|----------|------------|
| **Live / streaming** — append one candle at a time | **Hexital** |
| **Large bulk backtest** — load full history once, vectorise | **Pandas-TA** |

Hexital only calculates missing readings on append (O(1) per update). Libraries built on pandas typically recompute or reshape the full frame on each append, which gets slower as history grows.

In internal benchmarks, Hexital stays roughly flat as candle count increases during incremental updates, while Pandas-TA time grows with series length. For bulk calculation on large static datasets, Pandas-TA is often faster.

![Chart of bulk calculations.](imgs/MACD_26_12_Bulk.png)
![Chart of all calculations.](imgs/EMA_10.png)

More detail and charts: [Features](features.md).

---

## Learn more

- [Features](features.md) — chaining, custom indicators, multi-timeframe, benchmarks
- [API Reference](reference/index.md)
- [Design & alternatives](about/design.md) — vs Pandas-TA and TALipp

---

## License

MIT — see [LICENSE](../LICENSE).
