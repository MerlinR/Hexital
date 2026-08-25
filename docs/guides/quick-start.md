# Quick Start

**Start here.** This page covers one indicator, a stream of candles, and reading the latest value. You do not need `Hexital`, timeframes, or custom indicators yet.

For the next steps, see [Choose your path](../index.md#choose-your-path) on the home page.

---

## Your first indicator

Hexital is built for **incremental** updates: append a candle, get the new reading — without recalculating the full history.

```python
from hexital import EMA, Candle

candles = Candle.from_dicts([
    {"open": 17213, "high": 2395, "low": 7813, "close": 3615, "volume": 19661},
    {"open": 1301, "high": 3007, "low": 11626, "close": 19048, "volume": 28909},
    {"open": 12615, "high": 923, "low": 7318, "close": 1351, "volume": 33765},
])

ema = EMA(candles=candles, period=3)
ema.calculate()

print(ema.reading())  # latest EMA value
```

### Append a new candle

Call `append()` when new market data arrives. The indicator recalculates automatically — you do not need to call `calculate()` again.

```python
ema.append(
    Candle.from_dict(
        {"open": 19723, "high": 4837, "low": 11631, "close": 6231, "volume": 38993}
    )
)
print(ema.reading())
```

!!! tip "Indicator names"
    If you omit `name`, Hexital generates one from the indicator type and settings — e.g. `EMA_3` for `EMA(period=3)`. Use that name with `reading()`, `series()`, and analysis helpers. For nested dict outputs, use `:` — e.g. `MACD_12_26_9:signal`.

---

## Live trading

Hexital **does not fetch candles** — your exchange, websocket, or database layer delivers OHLCV. Hexital tells you **how much history you need**, accepts `append()` / `prepend()`, and keeps indicators incremental from there.

Typical bootstrap:

```python
from hexital import EMA, RSI, Candle, Hexital

strategy = Hexital("live", [], [EMA(period=10), RSI(period=14)])

# 1. Your feed decides what to request (Hexital only advises bar counts)
prefetch = strategy.minimum_candles_by_timeframe()
# e.g. {"DEFAULT": 15}  → fetch 15 bars on your default stream

history = fetch_from_your_exchange(count=prefetch["DEFAULT"])  # not Hexital

# 2. Load history, then check readiness on Hexital's side
for candle in history:
    strategy.append(candle)

if strategy.has_sufficient_candles():
    strategy.calculate()

# 3. Live loop — append recalculates automatically
while True:
    strategy.append(await next_candle_from_feed())
    if strategy.exists("RSI_14"):  # valid latest reading
        ...
```

| Step | Your code | Hexital |
|------|-----------|---------|
| How many bars to fetch? | Read `minimum_candles_by_timeframe()` | Per-series bar counts |
| Enough loaded yet? | `has_sufficient_candles()` | Compares bar count to each indicator's `minimum_candles` |
| First full calc | `calculate()` once after history | Fills missing readings |
| Each new tick | `append(candle)` | Incremental update |

Multi-timeframe strategies: fetch **each series separately** using the matching key from `minimum_candles_by_timeframe()` (e.g. `"DEFAULT"` vs `"T10"`). See [History and readiness](hexital-indepth.md#history-and-readiness).

Persisting candles **with** indicator readings: [Serialisation](../features.md#serialisation) and [Readings on candles](candles.md#readings-on-candles).

---

## Candles

Every indicator works on [Candle][hexital.core.candle.Candle] objects. The minimum fields are `open`, `high`, `low`, `close`, and `volume`.

The quickest path for bulk data is usually a list of dicts:

```python
candles = Candle.from_dicts([
    {"open": 1.0, "high": 1.2, "low": 0.9, "close": 1.1, "volume": 1000},
])
```

You can also pass dicts or lists directly to `append()` — Hexital converts them for you.

For every input format (lists, timestamps, Pandas, and more), see the [Candles guide](candles.md).

---

## What next?

| Goal | Guide |
|------|-------|
| Live feed bootstrap (history + append) | [Live trading](#live-trading) above |
| Run several indicators on one candle stream | [Hexital strategies](hexital-indepth.md) |
| Typed indicator access (`HexitalCol`) | [Hexital strategies](hexital-indepth.md#indicatorcollection) |
| Save and restore strategy config | [Hexital strategies](hexital-indepth.md#saving-and-restoring-a-strategy) |
| Trim memory, timestamps, timeframes | [Candles](candles.md) |
| Export candles with readings | [Candles](candles.md#readings-on-candles) |
| Crossovers, rising/falling checks | [Analysis](analysis-indepth.md) |
| Write your own indicator | [Custom indicators](custom-indicator.md) |
