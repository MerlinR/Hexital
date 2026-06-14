from __future__ import annotations

import random
from collections.abc import Callable, Sequence
from datetime import datetime, timedelta
from pathlib import Path
from time import perf_counter
from typing import Any

import matplotlib
import pandas as pd
import pandas_ta as ta

from hexital import Candle, Hexital

matplotlib.use("Agg")

import matplotlib.pyplot as plt

OUTPUT_DIR = Path("benchmarks/speed_tests")
BASE_TIMESTAMP = datetime(2032, 1, 1)
DEFAULT_REPEATS = 3
DEFAULT_MAX_POINTS = 40

StrategyConfig = list[dict[str, Any]]
BenchmarkFn = Callable[[list[dict[str, Any]], StrategyConfig], float]


def generate_random_candles(
    count: int, *, seed: int = 0, start: datetime = BASE_TIMESTAMP
) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    candles: list[dict[str, Any]] = []

    for index in range(count):
        candles.append(
            {
                "open": rng.randint(0, 9_000_000),
                "high": rng.randint(0, 9_000_000),
                "low": rng.randint(0, 9_000_000),
                "close": rng.randint(0, 9_000_000),
                "volume": rng.randint(0, 10_000),
                "timestamp": start + timedelta(minutes=index),
            }
        )

    return candles


def build_dataframe(candles: Sequence[dict[str, Any]]) -> pd.DataFrame:
    frame = pd.DataFrame.from_records(candles)
    frame.set_index("timestamp", inplace=True)
    return frame


def build_pandas_strategy(strategy: StrategyConfig) -> ta.Strategy:
    return ta.Strategy(name="benchmark", ta=strategy)


def plot_results(results: dict[str, list[float]], title: str, ylabel: str) -> None:
    plt.figure()

    for key, values in results.items():
        if key == "count":
            continue
        plt.plot(results["count"], values, label=key)

    plt.xlabel("Candles Count")
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / f"{title}.png")
    plt.close()


def save_results_csv(results: dict[str, list[float]], title: str) -> None:
    pd.DataFrame(results).to_csv(OUTPUT_DIR / f"{title}.csv", index=False)


def mean_runtime(
    benchmark: BenchmarkFn,
    candles: list[dict[str, Any]],
    strategy: StrategyConfig,
    repeats: int,
) -> float:
    total = 0.0

    for _ in range(repeats):
        total += benchmark(candles, strategy)

    return round(total / repeats, 6)


def build_sample_counts(
    candle_count: int, step: int, max_points: int = DEFAULT_MAX_POINTS
) -> list[int]:
    counts = list(range(step, candle_count + 1, step))

    if len(counts) <= max_points:
        return counts

    sample_counts: list[int] = []
    last_index = len(counts) - 1

    for point_index in range(max_points):
        target_index = round(point_index * last_index / (max_points - 1))
        value = counts[target_index]
        if not sample_counts or value != sample_counts[-1]:
            sample_counts.append(value)

    if sample_counts[-1] != counts[-1]:
        sample_counts.append(counts[-1])

    return sample_counts


def build_seed_map(counts: Sequence[int]) -> dict[int, int]:
    return {count: index for index, count in enumerate(counts, start=1)}


def warmup_benchmark(
    counts: Sequence[int],
    seed_map: dict[int, int],
    hexital_strategy: StrategyConfig,
    pandas_strategy: StrategyConfig,
    *,
    include_incremental: bool,
) -> None:
    warmup_count = min(counts)
    warmup_candles = generate_random_candles(warmup_count + 1, seed=seed_map[warmup_count])

    benchmark_hexital_bulk(warmup_candles[:warmup_count], hexital_strategy)
    benchmark_pandas_bulk(warmup_candles[:warmup_count], pandas_strategy)

    if include_incremental:
        benchmark_hexital_incremental(warmup_candles, hexital_strategy)
        benchmark_pandas_incremental(warmup_candles, pandas_strategy)


def benchmark_hexital_bulk(
    candles: list[dict[str, Any]], strategy: StrategyConfig
) -> float:
    hexital = Hexital("benchmark", Candle.from_dicts(candles), strategy)
    start = perf_counter()
    hexital.calculate()
    return perf_counter() - start


def benchmark_pandas_bulk(
    candles: list[dict[str, Any]], strategy: StrategyConfig
) -> float:
    frame = build_dataframe(candles)
    pandas_strategy = build_pandas_strategy(strategy)
    start = perf_counter()
    frame.ta.strategy(pandas_strategy)
    return perf_counter() - start


def benchmark_hexital_incremental(
    candles: list[dict[str, Any]], strategy: StrategyConfig
) -> float:
    history = Candle.from_dicts(candles[:-1])
    next_candle = Candle.from_dict(candles[-1])

    hexital = Hexital("benchmark", history, strategy)
    hexital.calculate()

    start = perf_counter()
    hexital.append(next_candle)
    return perf_counter() - start


def benchmark_pandas_incremental(
    candles: list[dict[str, Any]], strategy: StrategyConfig
) -> float:
    history = build_dataframe(candles[:-1])
    next_row = build_dataframe(candles[-1:])
    pandas_strategy = build_pandas_strategy(strategy)

    history.ta.strategy(pandas_strategy)

    start = perf_counter()
    updated = pd.concat([history, next_row])
    updated.ta.strategy(pandas_strategy)
    return perf_counter() - start


def build_result_store(include_incremental: bool) -> dict[str, list[float]]:
    results: dict[str, list[float]] = {
        "count": [],
        "Hexital Bulk": [],
        "Pandas_TA Bulk": [],
    }

    if include_incremental:
        results["Hexital Incremental"] = []
        results["Pandas_TA Incremental"] = []

    return results


def run_comparison(
    title: str,
    candle_count: int,
    step: int,
    hexital_strategy: StrategyConfig,
    pandas_strategy: StrategyConfig,
    *,
    include_incremental: bool,
    repeats: int = DEFAULT_REPEATS,
    max_points: int = DEFAULT_MAX_POINTS,
) -> None:
    results = build_result_store(include_incremental=include_incremental)
    counts = build_sample_counts(candle_count, step, max_points=max_points)
    seed_map = build_seed_map(counts)

    warmup_benchmark(
        counts,
        seed_map,
        hexital_strategy,
        pandas_strategy,
        include_incremental=include_incremental,
    )

    for count in counts:
        print(f"{title}: candles={count}")
        candles = generate_random_candles(count + 1, seed=seed_map[count])
        results["count"].append(count)

        results["Hexital Bulk"].append(
            mean_runtime(
                benchmark_hexital_bulk,
                candles[:count],
                hexital_strategy,
                repeats,
            )
        )
        results["Pandas_TA Bulk"].append(
            mean_runtime(
                benchmark_pandas_bulk,
                candles[:count],
                pandas_strategy,
                repeats,
            )
        )

        if include_incremental:
            results["Hexital Incremental"].append(
                mean_runtime(
                    benchmark_hexital_incremental,
                    candles,
                    hexital_strategy,
                    repeats,
                )
            )
            results["Pandas_TA Incremental"].append(
                mean_runtime(
                    benchmark_pandas_incremental,
                    candles,
                    pandas_strategy,
                    repeats,
                )
            )

    save_results_csv(results, title)
    plot_results(results, title, "Time (Seconds)")


def run_test_ema(candle_count: int, step: int) -> None:
    run_comparison(
        title="EMA_10",
        candle_count=candle_count,
        step=step,
        hexital_strategy=[{"indicator": "EMA"}],
        pandas_strategy=[{"kind": "ema"}],
        include_incremental=True,
    )


def run_test_supertrend(candle_count: int, step: int) -> None:
    run_comparison(
        title="Supertrend_7",
        candle_count=candle_count,
        step=step,
        hexital_strategy=[{"indicator": "Supertrend"}],
        pandas_strategy=[{"kind": "supertrend"}],
        include_incremental=True,
    )


def run_test_macd_bulk_only(candle_count: int, step: int, repeats: int) -> None:
    run_comparison(
        title="MACD_26_12_Bulk",
        candle_count=candle_count,
        step=step,
        hexital_strategy=[{"indicator": "MACD"}],
        pandas_strategy=[{"kind": "macd"}],
        include_incremental=False,
        repeats=repeats,
        max_points=30,
    )


def run_tests() -> None:
    run_test_ema(5_000, 100)
    run_test_supertrend(5_000, 100)
    run_test_macd_bulk_only(50_000, 500, repeats=3)


if __name__ == "__main__":
    run_tests()
