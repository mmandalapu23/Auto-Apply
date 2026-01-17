.PHONY: help install dev migrate test lint format

help:
	@echo "Available commands:"
	@echo "  make install    - Install dependencies"
	@echo "  make dev        - Start development server"
	@echo "  make migrate    - Run database migrations"
	@echo "  make test       - Run tests"
	@echo "  make lint       - Run linting"
	@echo "  make format     - Format code"

install:
	cd backend && uv sync

dev:
	docker-compose up -d
	cd backend && uvicorn app.main:app --reload

migrate:
	cd backend && alembic upgrade head

test:
	cd backend && pytest

lint:
	cd backend && ruff check app/

format:
	cd backend && ruff format app/

clean:
	docker-compose down -v
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
