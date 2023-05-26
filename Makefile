SHELL := /bin/bash

all: test

clean:
	@echo "Cleaning up"
	rm -rf .venv

setup:
	@echo "Running setup"
	poetry update

lint:
	pylint --disable=C0116,C0114,C0115,E0401 --max-line-length=90 ./hexital


test:
	@echo "Running Tests"
	poetry run pytest -vv --asyncio-mode=strict --cov=hexital

test-all:
	@echo "Running Tests"
	poetry run coverage run --omit="tests/*" -m pytest -vv --asyncio-mode=strict
	poetry run coverage report -m