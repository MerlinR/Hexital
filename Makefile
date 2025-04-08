SHELL := /bin/bash

all: test

setup:
	@echo "Running setup"
	poetry install --with dev

format:
	poetry run ruff format hex*

update:
	@echo "Running setup"
	poetry update

lock:
	@echo "Running setup"
	poetry lock

build:
	@echo "Building package"
	poetry build

truth:
	@echo "Generating source of truth"
	poetry install --with truth
	poetry run python tests/data/generate_source_of_truth.py 


speed_test:
	@echo "Running Speed tests"
	poetry install --with speed_tests
	poetry run python tests/extra/speed_tests/run_speed_tests.py 


new-test-candles:
	@echo "Generating New Source data"
	poetry install --with truth
	poetry run python tests/data/generate_new_data.py 

test:
	@echo "Running Tests"
	poetry run pytest -vv --cov=hexital --durations=0

test-all:
	@echo "Running Tests"
	poetry run coverage run --omit="tests/*" -m pytest -vv --durations=0
	poetry run coverage report -m

profile:
	poetry run python3 tests/extra/profiling/profile_tests.py
	poetry run snakeviz prof/


docs:
	@echo "Generating Docs"
	poetry install --with docs
