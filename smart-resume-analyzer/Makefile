# ──────────────────────────────────────────────────────────────
# Smart Resume Analyzer — Makefile
# ──────────────────────────────────────────────────────────────

.PHONY: install dev prod migrate test seed logs shell clean lint help

# ─── Help ─────────────────────────────────────────────────────
help: ## Show this help
	@echo "Smart Resume Analyzer — Available commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

# ─── Install ─────────────────────────────────────────────────
install: ## Install backend + frontend dependencies
	cd backend && pip install -r requirements.txt
	cd frontend && npm install

# ─── Dev ──────────────────────────────────────────────────────
dev: ## Start all services in development mode
	docker-compose up --build

dev-bg: ## Start all services in background
	docker-compose up --build -d

# ─── Prod ─────────────────────────────────────────────────────
prod: ## Start production deployment
	docker-compose -f docker-compose.prod.yml up -d --build

prod-down: ## Stop production deployment
	docker-compose -f docker-compose.prod.yml down

# ─── Database ─────────────────────────────────────────────────
migrate: ## Run Alembic migrations
	docker-compose exec backend alembic upgrade head

migration: ## Create a new Alembic migration (usage: make migration msg="add users table")
	docker-compose exec backend alembic revision --autogenerate -m "$(msg)"

# ─── Testing ─────────────────────────────────────────────────
test: ## Run backend tests with coverage
	docker-compose exec backend pytest -v --cov=app --cov-report=term-missing

test-local: ## Run backend tests locally (no Docker)
	cd backend && pytest -v --cov=app --cov-report=term-missing

# ─── Seed Data ───────────────────────────────────────────────
seed: ## Seed database with sample data
	docker-compose exec backend python scripts/seed_data.py

# ─── Logs ─────────────────────────────────────────────────────
logs: ## Follow backend logs
	docker-compose logs -f backend

logs-all: ## Follow all service logs
	docker-compose logs -f

# ─── Shell ────────────────────────────────────────────────────
shell: ## Open bash shell in backend container
	docker-compose exec backend bash

psql: ## Open psql shell in postgres container
	docker-compose exec postgres psql -U $${POSTGRES_USER:-sra_user} -d $${POSTGRES_DB:-smart_resume}

# ─── Lint ─────────────────────────────────────────────────────
lint: ## Lint backend and frontend
	cd backend && python -m flake8 app/ --max-line-length=120 --exclude=__pycache__
	cd frontend && npm run lint 2>/dev/null || true

# ─── Cleanup ─────────────────────────────────────────────────
clean: ## Stop containers, remove volumes
	docker-compose down -v
	docker-compose -f docker-compose.prod.yml down -v 2>/dev/null || true
	rm -rf frontend/dist backend/__pycache__

# ─── Status ───────────────────────────────────────────────────
status: ## Show running containers
	docker-compose ps
