.PHONY: install fmt lint test check run up down migrate revision

install:
	pip install -e ".[dev]"
	pre-commit install

fmt:
	black .
	isort .

lint:
	black --check .
	isort --check-only .
	pylint app tests
	mypy app tests

test:
	pytest

check: lint test

run:
	uvicorn app.main:app --reload

up:
	docker compose -f infra/compose/compose.yaml up -d --build

down:
	docker compose -f infra/compose/compose.yaml down

migrate:
	alembic upgrade head

revision:
	alembic revision --autogenerate -m "$(m)"
