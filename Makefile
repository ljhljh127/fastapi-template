.PHONY: install fmt lint test check drift run up down migrate revision

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

# DB가 떠 있어야 한다
drift:
	alembic upgrade head
	alembic check

run:
	uvicorn app.main:app --reload

up:
	docker compose -f infra/compose/compose.yaml up -d --build

down:
	docker compose -f infra/compose/compose.yaml down

migrate:
	alembic upgrade head

revision:
	@test -n "$(m)" || (echo 'usage: make revision m="create order table"'; exit 1)
	alembic revision --autogenerate -m "$(m)"
