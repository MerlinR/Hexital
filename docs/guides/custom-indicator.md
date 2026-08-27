# Guide: Creating an Indicator

!!! note "Advanced"
    You do not need this page for basic usage. Start with [Quick Start](quick-start.md) if you are new to Hexital.

All built-in indicators are dataclasses that subclass [Indicator][hexital.core.indicator.Indicator] and implement `_calculate_reading()`. Readings are stored on each [Candle][hexital.core.candle.Candle] and updated incrementally on `append()`.

---

## Which recipe do I need?

```
Need hidden state between candles?        → Recipe B (`add_state()`)
Need other indicators as inputs?          → Recipe C (child indicators)
Combine conditions into a signal?         → Recipe D ([signal indicators](#recipe-d--signal-indicator))
Just math on candle fields?               → Recipe A (single method)
One-off pattern without a full class?     → Amorph
Warm-up differs from `period`?            → [Minimum candles](#minimum-candles) (`_minimum_candles()`)
```

| Pattern | Built-in example | Child helpers |
|---------|------------------|---------------|
| Simple | [SMA][hexital.indicators.sma.SMA] | — |
| Stateful | [RSI][hexital.indicators.rsi.RSI] | `add_child_managed()` |
| Composite | [BBANDS][hexital.indicators.bbands.BBANDS] | `add_child()` |
| Signal | Custom entry/exit rules | `add_child()`, [hexital.analysis.signals][hexital.analysis.signals] |

---

## Generated names

Hexital builds `indicator.name` automatically in `_generate_name()` from `_name_parts()`. You normally **do not** override `_generate_name()`.

| Behaviour | Detail |
|-----------|--------|
| Default parts | `period` and `source`, when those fields exist on the indicator |
| Default `source` | Omitted from the name (e.g. `"close"` → `SMA_10`, not `SMA_10_close`) |
| Extra parameters | Override `_name_parts()` to list the dataclass fields to include |
| Nested outputs | Read with `:` — e.g. `strategy.reading("MACD_12_26_9:signal")` |
| `:` in names | Replaced with `-` in generated indicator names (nested paths still use `:` at lookup time) |

```python
def _name_parts(self) -> list[str]:
    return ["period", "multiplier", "source"]
```

Override `_format_name_part()` on `Indicator` only when a field needs special formatting (e.g. `timedelta` anchors on VWAP).

---

## Recipe A — Simple indicator

Use when the reading depends only on candle fields and prior readings of **this** indicator — no hidden state, no sub-indicators.

Based on [SMA][hexital.indicators.sma.SMA]:

```python
from dataclasses import dataclass, field

from hexital import Indicator


@dataclass(kw_only=True)
class MyAverage(Indicator[float | None]):
    _name: str = field(init=False, default="MyAverage")
    period: int = 10
    source: str = "close"

    def _calculate_reading(self, index: int) -> float | None:
        if self.prev_exists():
            prev = self.prev_reading()
            old = self.reading(self.source, index - self.period)
            new = self.reading(self.source)
            if prev is not None and old is not None and new is not None:
                return prev - (old - new) / self.period
            return None

        if self.reading_period(self.period, self.source):
            return self.candles_average(self.period, self.source)

        return None
```

Useful inherited helpers inside `_calculate_reading()`:

- `self.reading(source)` — value at the current index
- `self.prev_reading(source)` — value at the previous index
- `self.reading_period(n, source)` — enough history available?
- `self.candles_average(n, source)` — bootstrap the first reading

---

## Recipe B — Stateful indicator

Use when you need to **remember values between candles** that are not part of the public output — smoothed gains/losses, intermediate EMA inputs, etc.

Based on [RSI][hexital.indicators.rsi.RSI]:

```python
from dataclasses import dataclass, field

from hexital import Indicator, State


@dataclass(kw_only=True)
class MyOscillator(Indicator[float | None]):
    _name: str = field(init=False, default="MyOscillator")
    period: int = 14
    source: str = "close"

    def _initialise(self):
        self._state = self.add_state()

    def _calculate_reading(self, index: int) -> float | None:
        gains = None
        losses = None

        if self.prev_exists():
            change = self.prev_src() - self.src()
            change_gain = -change if change < 0 else 0.0
            change_loss = change if change > 0 else 0.0

            gains = (
                (self._state.prev("gain") * (self.period - 1)) + change_gain
            ) / self.period

            losses = (
                (self._state.prev("loss") * (self.period - 1)) + change_loss
            ) / self.period

        self._state.update(gain=gains, loss=losses)

        if gains is not None and losses is not None:
            return 100.0 - (100.0 / (1.0 + (gains / losses)))

        return None
```

- `add_state()` holds hidden state via `set()` / `update()` / `prev()`
- `src()` / `prev_src()` — shorthand for reading your configured `source` field
- `close`, `open`, etc. — OHLCV properties; `prev("close")`, `at(-2, "high")` for indexed reads
- `add_child_managed()` — child runs only when you invoke it (via `set_reading()` or `calculate_index()`)

---

## Minimum candles

Declare how many bars your indicator needs before it can produce a reading. Hexital uses this for exchange prefetch and readiness checks.

See [History and readiness](history-and-readiness.md) for the full prefetch workflow, strategy helpers, and common mistakes.

### Default behaviour

If your indicator has a `period` field, [Indicator][hexital.core.indicator.Indicator] defaults to `minimum_candles == period`. You do **not** need an override for a plain SMA-style indicator.

Composites that use `add_child()` inherit aggregation automatically — `minimum_candles` becomes the max of your override (or default) and every child's `minimum_candles`.

### When to override `_minimum_candles()`

Override when warm-up differs from `period`:

```python
def _minimum_candles(self) -> int:
    return self.period + 1   # e.g. RSI-style: first reading one bar after period window
```

Other common cases:

| Case | Example | Override |
|------|---------|----------|
| Single-bar transform | HLA, HLCA | `return 1` |
| Needs prior bar | TR, PivotPoints | `return 2` |
| Composite formula | MACD, TEMA | Custom sum/product of child periods |
| No history field | OBV, VWAP | Explicit constant |

```python
@dataclass(kw_only=True)
class MyOscillator(Indicator[float | None]):
    period: int = 14

    def _minimum_candles(self) -> int:
        return self.period + 1

    def _calculate_reading(self, index: int) -> float | None:
        ...
```

### Composites

You usually **do not** override on composites — child `minimum_candles` values are aggregated. Override only when the parent's first valid reading lags behind children:

```python
def _minimum_candles(self) -> int:
    return 0   # rely on max(child.minimum_candles ...)
```

Inspect children with `minimum_candles_by_indicator()` while developing.

---

## Recipe C — Composite indicator

Use when your indicator **depends on other indicators** (moving averages, standard deviation, ATR, etc.).

Based on [BBANDS][hexital.indicators.bbands.BBANDS]:

```python
from dataclasses import dataclass, field

from hexital import Indicator
from hexital import SMA, STDEV


@dataclass(kw_only=True)
class MyBands(Indicator[dict[str, float | None]]):
    _name: str = field(init=False, default="MyBands")
    period: int = 5
    source: str = "close"
    _std: float = field(init=False, default=2.0)

    def _initialise(self):
        self.sub_stdev = self.add_child(STDEV(source=self.source, period=self.period))
        self.sub_sma = self.add_child(SMA(source=self.source, period=self.period))

    def _calculate_reading(self, index: int) -> dict[str, float | None]:
        if not (self.sub_sma.exists() and self.sub_stdev.exists()):
            return {"lower": None, "mid": None, "upper": None}

        sma = self.sub_sma.reading()
        stdev = self.sub_stdev.reading()

        return {
            "mid": sma,
            "lower": sma - (stdev * self._std),
            "upper": sma + (stdev * self._std),
        }
```

### Child timing

| Method | When it runs |
|--------|----------------|
| `add_child(...)` | Before parent's `_calculate_reading()` (default) |
| `add_child_after(...)` | After the parent's reading is stored |
| `add_child_managed(...)` | Only when you call it explicitly |

For full control, pass `when=` using [ChildWhen][hexital.core.indicator.ChildWhen]:

```python
from hexital import ChildWhen

self.sub_signal = self.add_child(EMA(...), when=ChildWhen.MANUAL)
```

---

## Recipe D — Signal indicator

Use when you want a **stable, incremental signal** — entry/exit rules, alerts, or filters — composed from child indicators and [analysis][hexital.analysis] helpers. The signal is just another indicator: readings live on candles, append stays O(1), and the signal serialises with [Hexital.settings](hexital-indepth.md#saving-and-restoring-a-strategy).

[hexital.analysis.signals][hexital.analysis.signals] provides small composition helpers:

| Helper | Purpose |
|--------|---------|
| [edge()][hexital.analysis.signals.edge] | True when a condition turns on this bar |
| [falling_edge()][hexital.analysis.signals.falling_edge] | True when a condition turns off this bar |
| [level_edge()][hexital.analysis.signals.level_edge] | Same as `edge()` for level conditions |
| [level_falling_edge()][hexital.analysis.signals.level_falling_edge] | Same as `falling_edge()` for level conditions |
| [crossed_above()][hexital.analysis.signals.crossed_above] | Reading crossed up through a fixed level |
| [crossed_below()][hexital.analysis.signals.crossed_below] | Reading crossed down through a fixed level |
| [between()][hexital.analysis.signals.between] | Reading is within an inclusive range |
| [all_of()][hexital.analysis.signals.all_of] | Every condition must be `True` |
| [any_of()][hexital.analysis.signals.any_of] | At least one condition is `True` |
| [none_of()][hexital.analysis.signals.none_of] | No condition is `True` |

For crossing on historical windows, use [crossover_level()][hexital.analysis.movement.crossover_level] / [crossunder_level()][hexital.analysis.movement.crossunder_level]. For a single bar pair inside `_calculate_reading()`, use the scalar helpers in [hexital.analysis.signals][hexital.analysis.signals].

```python
from dataclasses import dataclass, field

from hexital import EMA, Indicator, RSI
from hexital.analysis.signals import all_of, crossed_above, level_edge, level_falling_edge


@dataclass(kw_only=True)
class RsiCrossAboveEma(Indicator[bool | None]):
    _name: str = field(init=False, default="RsiCrossAboveEma")
    rsi_period: int = 14
    ema_period: int = 20
    rsi_level: float = 30.0

    def _initialise(self):
        self.rsi = self.add_child(RSI(period=self.rsi_period))
        self.ema = self.add_child(EMA(period=self.ema_period))

    def _calculate_reading(self, index: int) -> bool | None:
        rsi = self.rsi.reading()
        ema = self.ema.reading()
        prev_rsi = self.rsi.prev_reading()

        if rsi is None or ema is None or prev_rsi is None:
            return None

        return all_of(
            crossed_above(rsi, prev_rsi, self.rsi_level),
            self.close > ema,
        )


@dataclass(kw_only=True)
class RsiCrossSignal(Indicator[dict[str, bool | None]]):
    """Expose both level (while true) and edge (on transition) readings."""
    _name: str = field(init=False, default="RsiCrossSignal")
    rsi_level: float = 30.0

    def _initialise(self):
        self.rsi = self.add_child(RSI(period=14))

    def _calculate_reading(self, index: int) -> dict[str, bool | None]:
        rsi = self.rsi.reading()
        prev_rsi = self.rsi.prev_reading()

        if rsi is None or prev_rsi is None:
            return {"level": None, "edge": None}

        level = rsi < self.rsi_level
        prev = self.prev_reading(default={})
        prev_level = prev.get("level") if isinstance(prev, dict) else None

        return {
            "level": level,
            "edge": level_edge(level, prev_level),
            "exit": level_falling_edge(level, prev_level),
        }
```

Register on [Hexital][hexital.core.hexital.Hexital] like any indicator:

```python
strategy = Hexital("signals", candles, [RsiCrossAboveEma(), RsiCrossSignal()])
strategy.calculate()

if strategy.reading("RsiCrossAboveEma"):
    ...
if strategy.reading("RsiCrossSignal:edge"):
    ...
```

**Bar-close semantics:** signals evaluate when a candle is appended. Only append closed bars from your feed if you want close-only entries.

---

## Amorph — functions as indicators

For one-off signals or pattern checks without writing a full class, use [Amorph][hexital.indicators.amorph.Amorph]:

```python
from hexital import Amorph
from hexital.analysis.patterns import doji

pattern = Amorph(analysis=doji)
pattern.append(candles)
pattern.calculate()
```

### Prefetch hints on Amorph

Amorph resolves `minimum_candles` from analysis kwargs:

| Kwarg | Used for |
|-------|----------|
| `minimum_candles` | Explicit prefetch count (not forwarded to the analysis function) |
| `period` | Warm-up when the wrapped function accepts `period` |
| `lookback` | Window size; combined with `period` as `period + lookback - 1` when both are set |

For [doji][hexital.analysis.patterns.doji] without kwargs, `minimum_candles` is `0` — pass `minimum_candles=11` (or wrap with a function that accepts `period`) when prefetching matters.

```python
Amorph(analysis=doji, minimum_candles=11)
Amorph(analysis=doji, lookback=20, minimum_candles=30)
```

---

## Using a custom indicator in Hexital

```python
from hexital import Candle, Hexital

from my_indicators import MyBands

strategy = Hexital("demo", candles, [MyBands(period=20)])
strategy.append(new_candle)
print(strategy.reading("MyBands_20"))
```

See also the [Features — Custom Indicators](../features.md#custom-indicators) example.
