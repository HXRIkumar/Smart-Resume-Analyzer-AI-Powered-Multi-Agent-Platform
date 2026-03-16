.PHONY: install dev migrate test docker-up docker-down lint format clean

# ─── Install all dependencies ───
install:
	@echo "📦 Installing backend dependencies..."
	cd backend && pip install -r requirements.txt
	@echo "📦 Installing frontend dependencies..."
	cd frontend && npm install
	@echo "✅ All dependencies installed."

# ─── Start dev servers ───
dev:
	@echo "🚀 Starting development servers..."
	@make -j2 dev-backend dev-frontend

dev-backend:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	cd frontend && npm run dev

# ─── Database migrations ───
migrate:
	@echo "🗃️  Running Alembic migrations..."
	cd backend && alembic upgrade head

migrate-generate:
	@echo "🗃️  Generating new migration..."
	cd backend && alembic revision --autogenerate -m "$(msg)"

# ─── Run tests ───
test:
	@echo "🧪 Running backend tests..."
	cd backend && pytest -v --tb=short

test-cov:
	@echo "🧪 Running tests with coverage..."
	cd backend && pytest --cov=app --cov-report=html -v

# ─── Docker ───
docker-up:
	@echo "🐳 Starting Docker containers..."
	docker compose up --build -d

docker-down:
	@echo "🐳 Stopping Docker containers..."
	docker compose down

docker-logs:
	docker compose logs -f

# ─── Linting ───
lint:
	@echo "🔍 Running ruff linter..."
	cd backend && ruff check app/ tests/

format:
	@echo "✨ Formatting code..."
	cd backend && ruff format app/ tests/

# ─── Cleanup ───
clean:
	@echo "🧹 Cleaning up..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	rm -rf backend/htmlcov backend/.coverage
	@echo "✅ Clean complete."
