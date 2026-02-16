PYTHON ?= python3
PIP ?= $(PYTHON) -m pip
COMPOSE_FILE ?= infra/docker/docker-compose.yml

.PHONY: install install-runtime install-dev lint type test run-backend run-frontend fmt pre-commit compose-up compose-up-with-ollama compose-down compose-build compose-logs compose-config

install:
	$(PIP) install -e .

install-runtime:
	$(PIP) install -e .[speech]

install-dev:
	$(PIP) install -e .[dev]

lint:
	ruff check backend
	ruff format --check backend

type:
	mypy backend/app backend/tests

test:
	pytest

fmt:
	ruff check backend --fix
	ruff format backend

run-backend:
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

run-frontend:
	cd frontend && npm install && npm run dev

pre-commit:
	pre-commit run --all-files

compose-up:
	docker compose -f $(COMPOSE_FILE) up -d --no-build backend frontend

compose-up-with-ollama:
	docker compose -f $(COMPOSE_FILE) --profile with-ollama up -d --no-build

compose-down:
	docker compose -f $(COMPOSE_FILE) down

compose-build:
	docker compose -f $(COMPOSE_FILE) build

compose-logs:
	docker compose -f $(COMPOSE_FILE) logs -f

compose-config:
	docker compose -f $(COMPOSE_FILE) config
