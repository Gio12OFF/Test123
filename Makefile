.PHONY: install test lint format run docker

install:
	python -m pip install -e ".[api,dev]"

test:
	pytest --cov=streamprobe --cov-report=term-missing

lint:
	ruff check .
	ruff format --check .

format:
	ruff check --fix .
	ruff format .

run:
	streamprobe serve --host 0.0.0.0

docker:
	docker compose up --build
