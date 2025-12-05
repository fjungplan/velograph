# ChainLines - Backend Makefile
# Provides convenient shortcuts for common development tasks

.PHONY: help migrate migrate-rollback migrate-create test shell alembic-upgrade-local

help:
	@echo "Available commands:"
	@echo "  make migrate              - Run pending migrations"
	@echo "  make migrate-rollback     - Rollback one migration"
	@echo "  make migrate-create NAME='description' - Create new migration"
	@echo "  make test                 - Run tests"
	@echo "  make shell                - Open backend container shell"

migrate:
	@echo "Running database migrations..."
	docker-compose exec backend alembic upgrade head

migrate-rollback:
	@echo "Rolling back last migration..."
	docker-compose exec backend alembic downgrade -1

migrate-create:
	@if [ -z "$(NAME)" ]; then \
		echo "Error: NAME is required. Usage: make migrate-create NAME='description'"; \
		exit 1; \
	fi
	@echo "Creating new migration: $(NAME)"
	docker-compose exec backend alembic revision --autogenerate -m "$(NAME)"

test:
	@echo "Running tests with Python faulthandler enabled..."
	docker-compose exec backend python -X faulthandler -m pytest -q

shell:
	@echo "Opening backend container shell..."
	docker-compose exec backend sh

# Run Alembic migrations against a locally reachable DATABASE_URL
# Requires env var DATABASE_URL to be set, or a .env file resolvable by Alembic env.py
alembic-upgrade-local:
	@echo "Running Alembic migrations locally (using DATABASE_URL) ..."
	alembic upgrade head
