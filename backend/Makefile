.PHONY: help install dev migrate test lint format clean docker-build docker-up docker-down seed

help:
	@echo "AutoApply ATS - Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install       - Install dependencies in virtual environment"
	@echo "  make dev           - Start development server (with auto-reload)"
	@echo ""
	@echo "Database:"
	@echo "  make migrate       - Run database migrations"
	@echo "  make seed          - Seed database with demo data"
	@echo ""
	@echo "Testing & Quality:"
	@echo "  make test          - Run pytest"
	@echo "  make lint          - Run ruff linter"
	@echo "  make format        - Format code with black"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build  - Build Docker images"
	@echo "  make docker-up     - Start Docker services"
	@echo "  make docker-down   - Stop Docker services"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean         - Remove cache and temporary files"

install:
	python -m venv venv
	.\venv\Scripts\pip install -e ".[dev]"
	@echo "✓ Dependencies installed. Activate venv with: .\venv\Scripts\Activate.ps1"

dev:
	.\venv\Scripts\uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

migrate:
	.\venv\Scripts\alembic upgrade head

seed:
	.\venv\Scripts\python -c "import sys; sys.path.insert(0, '.'); from scripts.seed_db import main; main()"

test:
	.\venv\Scripts\pytest tests/ -v --cov=app --cov-report=html

lint:
	.\venv\Scripts\ruff check app/ tests/

format:
	.\venv\Scripts\black app/ tests/ --line-length=100

clean:
	Remove-Item -Path "__pycache__" -Recurse -ErrorAction SilentlyContinue
	Remove-Item -Path ".pytest_cache" -Recurse -ErrorAction SilentlyContinue
	Remove-Item -Path ".coverage" -Recurse -ErrorAction SilentlyContinue
	Remove-Item -Path "htmlcov" -Recurse -ErrorAction SilentlyContinue
	Remove-Item -Path "*.egg-info" -Recurse -ErrorAction SilentlyContinue

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down
