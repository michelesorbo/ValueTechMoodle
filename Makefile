.PHONY: help db up down migrate api web test lint

help: ## Mostra i comandi disponibili
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}'

db: ## Avvia solo PostgreSQL (sviluppo locale)
	docker compose up -d db

up: ## Avvia l'intero stack (http://localhost:8080)
	docker compose up -d --build

down: ## Ferma lo stack
	docker compose down

migrate: ## Applica le migrazioni Alembic
	cd backend && uv run alembic upgrade head

api: ## Backend in hot-reload su :8000
	cd backend && uv run fastapi dev app/main.py --port 8000

web: ## Frontend in hot-reload su :5173
	cd frontend && npm run dev

test: ## Test backend + frontend
	cd backend && uv run pytest -q
	cd frontend && npm test

lint: ## Lint e type-check
	cd backend && uv run ruff check . && uv run ruff format --check . && uv run mypy app
	cd frontend && npm run lint && npm run typecheck
