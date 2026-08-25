# Guide: Indicators

!!! note "Advanced"
    You do not need this page for basic usage. Start with [Quick Start](quick-start.md) if you are new to Hexital.

---

## Generated names

Unnamed indicators get a name from type + configuration. The base [Indicator][hexital.core.indicator.Indicator] builds this in `_generate_name()` using `_name_parts()`.

**Defaults**

- `_name_parts()` returns `period` and `source` when those fields exist
- Default `source` (usually `"close"`) is **not** included in the name
- A resample transform suffix is appended when `timeframe=` is set (e.g. `EMA_10_T5`)

**Examples**

| Construction | Generated name |
|--------------|----------------|
| `SMA(period=10)` | `SMA_10` |
| `EMA(period=3)` | `EMA_3` |
| `MACD()` | `MACD_12_26_9` |
| `EMA(period=10, timeframe="T5")` | `EMA_10_T5` |
| `SMA(period=10, source=hlca)` | `SMA_10_HLCA` |

Indicators with extra parameters override `_name_parts()` — see [Custom indicators](custom-indicator.md#generated-names).

### Nested dict outputs

Multi-value indicators store a dict on each candle. Read one field with `:`:

```python
macd = MACD(candles=candles)
macd.calculate()
print(macd.reading("MACD"))           # full dict on latest candle
print(strategy.reading("MACD_12_26_9:signal"))
```

### Series

| Old (removed) | Current |
|---------------|---------|
| `indicator.readings()` | `indicator.series()` |
| `hexital.reading_as_list(name)` | `hexital.series(name)` |
| `hexital.readings()` | `hexital.all_series()` |

---

## History and readiness

Before running `calculate()` — especially when prefetching from an exchange — you may need to know how many bars an indicator requires.

### `minimum_candles`

[Indicator.minimum_candles][hexital.core.indicator.Indicator.minimum_candles] is the **minimum bar count** before this indicator can produce a reading. The count is **1-based**: `15` means the **15th candle** is the first that may have a non-`None` value after `calculate()`.

| Value | Meaning |
|-------|---------|
| `period` (default) | Indicators with a `period` field inherit `minimum_candles == period` |
| `0` | Unknown — no `period` and no override (e.g. [Amorph][hexital.indicators.amorph.Amorph] without prefetch hints) |
| Custom | Override `_minimum_candles()` when warm-up differs from `period` (see [Custom indicators](custom-indicator.md#minimum-candles)) |

Composites aggregate over children — `minimum_candles` is the **maximum** of the indicator's own value and every child's `minimum_candles` (e.g. [MACD][hexital.indicators.macd.MACD], [BBANDS][hexital.indicators.bbands.BBANDS]).

```python
ema = EMA(period=10, candles=candles)
ema.minimum_candles   # 10

rsi = RSI(period=14, candles=candles)
rsi.minimum_candles   # 15  (period + 1)
```

### `is_ready`

[Indicator.is_ready][hexital.core.indicator.Indicator.is_ready] is `True` when loaded history meets `minimum_candles`:

```python
if ema.is_ready:
    ema.calculate()
```

When `minimum_candles` is `0`, `is_ready` is `True` as long as there is at least one candle.

### Child breakdown

[Indicator.minimum_candles_by_indicator()][hexital.core.indicator.Indicator.minimum_candles_by_indicator] returns each **child** indicator's `minimum_candles`, keyed by name — useful when inspecting composite warm-up:

```python
macd = MACD(candles=candles)
macd.minimum_candles_by_indicator()
# e.g. {"MACD_12_26_9_fast": 12, "MACD_12_26_9_slow": 26, ...}
```

Strategy-level prefetch and multi-timeframe checks live on [Hexital](hexital-indepth.md#history-and-readiness).

---

## Chaining

Hexital allows you to chain indicators together seamlessly. In a chain, the output of one indicator can serve as the input for another, enabling automated, indefinite chaining of calculations.

This feature provides significant flexibility for creating custom indicators. For example, you can use an EMA to smooth the output of another indicator or incorporate indicators within other indicators to enhance their calculations.

A practical example is the calculation of the [Stochastic Oscillator (STOCH)][hexital.indicators.stoch.STOCH]. The `k` value of STOCH is used as the input for an SMA to compute the `d` value. Internally, this is implemented as the STOCH indicator chaining the SMA indicator, using its own `k` value as the input source.

See also [Features — Indicator chaining](../features.md#indicator-chaining).
