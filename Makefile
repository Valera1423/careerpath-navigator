.PHONY: help up down build test lint fmt migrate revision logs shell

help:
	@echo "up         — поднять стек"
	@echo "down       — остановить стек"
	@echo "build      — пересобрать образы"
	@echo "test       — backend-тесты"
	@echo "lint       — backend-lint"
	@echo "fmt        — авто-формат"
	@echo "migrate    — применить миграции"
	@echo "revision   — новая миграция (m='message')"

up:
	docker compose up -d

down:
	docker compose down

build:
	docker compose up --build -d

test:
	cd backend && pytest

lint:
	cd backend && ruff check app tests && mypy app
	cd frontend && npm run typecheck

fmt:
	cd backend && ruff check --fix app tests && ruff format app tests

migrate:
	docker compose exec backend alembic upgrade head

revision:
	docker compose exec backend alembic revision --autogenerate -m "$(m)"

logs:
	docker compose logs -f backend frontend

shell:
	docker compose exec backend bash