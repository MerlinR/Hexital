SHELL := /bin/bash

all: test

setup:
	@echo "Running setup"
	uv sync

format:
	uv run ruff format hex*

update:
	@echo "Running setup"
	uv sync

lock:
	@echo "Running setup"
	uv lock --upgrade

build:
	@echo "Building package"
	uv build

truth:
	@echo "Generating source of truth"
	uv sync --group truth
	uv run python tests/data/generate_source_of_truth.py 

speed_test:
	@echo "Running Speed tests"
	uv sync --group speed_tests
	uv run python benchmarks/speed_tests/run_speed_tests.py 

new-test-candles:
	@echo "Generating New Source data"
	uv sync --group truth
	uv run python tests/data/generate_new_data.py 

test:
	@echo "Running Tests"
	uv run pytest -vv --cov=hexital --durations=0

test-all:
	@echo "Running Tests"
	uv run coverage run --omit="tests/*" -m pytest -vv --durations=0
	uv run coverage report -m

profile:
	uv run python3 benchmarks/profiling/profile_tests.py
	uv run snakeviz prof/

docs:
	@echo "Generating Docs"
	uv sync --group docs
