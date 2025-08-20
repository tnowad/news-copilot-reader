.PHONY: help dev backend frontend test lint format clean docker-up docker-down

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Development
dev: ## Start both backend and frontend in dev mode (requires make backend frontend in separate terminals)

backend: ## Start backend server
	cd news-copilot-backend && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && flask run

backend-prod: ## Start backend with gunicorn
	cd news-copilot-backend && gunicorn -w 4 -b 0.0.0.0:5000 "run:app"

frontend: ## Start frontend dev server
	cd news-copilot-frontend && pnpm install && pnpm dev

# Testing
test-backend: ## Run backend tests
	cd news-copilot-backend && python -m pytest tests/ -v

test-backend-cov: ## Run backend tests with coverage
	cd news-copilot-backend && python -m pytest tests/ -v --cov=app --cov-report=html --cov-report=term

test-frontend: ## Run frontend tests
	cd news-copilot-frontend && pnpm test

test: test-backend test-frontend ## Run all tests

# Linting & Formatting
lint-backend: ## Lint backend code
	cd news-copilot-backend && flake8 app/ && black --check app/ && isort --check-only app/

lint-frontend: ## Lint frontend code
	cd news-copilot-frontend && pnpm lint

format-backend: ## Format backend code
	cd news-copilot-backend && black app/ && isort app/

format-frontend: ## Format frontend code
	cd news-copilot-frontend && pnpm format

lint: lint-backend lint-frontend ## Run all linters
format: format-backend format-frontend ## Format all code

# Database
db-init: ## Initialize database
	cd news-copilot-backend && flask shell -c "from app import create_app; app = create_app(); from app.models import *; db.create_all()"

db-migrate: ## Run database migrations
	cd news-copilot-backend && flask db upgrade

db-seed: ## Seed database with sample data
	cd news-copilot-backend && flask shell -c "from app import create_app; app = create_app(); from app.seed import seed_database; seed_database()"

# Docker
docker-up: ## Start all services with Docker
	docker compose up --build

docker-down: ## Stop all Docker services
	docker compose down

docker-up-detached: ## Start all services in detached mode
	docker compose up --build -d

# Clean
clean: ## Remove build artifacts and caches
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	rm -rf news-copilot-frontend/.svelte-kit news-copilot-frontend/build
	rm -rf htmlcov .coverage coverage.xml
