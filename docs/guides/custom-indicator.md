# Guide: Creating an Indicator

!!! note "Advanced"
    You do not need this page for basic usage. Start with [Quick Start](quick-start.md) if you are new to Hexital.

All built-in indicators are dataclasses that subclass [Indicator][hexital.core.indicator.Indicator] and implement `_calculate_reading()`. Readings are stored on each [Candle][hexital.core.candle.Candle] and updated incrementally on `append()`.

---

## Which recipe do I need?

```
Need hidden state between candles?        → Recipe B (`add_state()`)
Need other indicators as inputs?          → Recipe C (child indicators)
Just math on candle fields?               → Recipe A (single method)
One-off pattern without a full class?     → Amorph
```

| Pattern | Built-in example | Child helpers |
|---------|------------------|---------------|
| Simple | [SMA][hexital.indicators.sma.SMA] | — |
| Stateful | [RSI][hexital.indicators.rsi.RSI] | `add_child_managed()` |
| Composite | [BBANDS][hexital.indicators.bbands.BBANDS] | `add_child()` |

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
| `fingerprint` | Stable hash of `settings` (+ `when` for children) for duplicate detection |

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

## Amorph — functions as indicators

For one-off signals or pattern checks without writing a full class, use [Amorph][hexital.indicators.amorph.Amorph]:

```python
from hexital import Amorph
from hexital.analysis.patterns import doji

pattern = Amorph(analysis=doji)
pattern.append(candles)
pattern.calculate()
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
