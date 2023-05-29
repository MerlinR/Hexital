SHELL := /bin/bash

all: test

setup:
	@echo "Running setup"
	poetry update

lint:
	pylint --disable=C0116,C0114,C0115,E0401 --max-line-length=90 ./hexital


test:
	@echo "Running Tests"
	poetry run pytest -vv --cov=hexital --durations=0

test-all:
	@echo "Running Tests"
	poetry run coverage run --omit="tests/*" -m pytest -vv --durations=0
	poetry run coverage report -m