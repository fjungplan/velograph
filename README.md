# Velograph
### The Cycling Team Lineage Timeline

An open-source visualization of the evolutionary history of professional cycling teams from 1900 to present.

## Overview

This project tracks the lineage of professional cycling teams through time, visualizing how teams evolve through rebrands, mergers, splits, and successions. The system uses a **Managerial Node** concept to represent the persistent legal entity that survives name changes.

### Key Features

- **Interactive Timeline Visualization**: Desktop D3.js "river" chart showing team evolution
- **Mobile-Optimized List View**: Chronological team history for mobile devices
- **Community-Driven**: Wiki-style editing with moderation system
- **Data Integrity**: Tracks team eras, sponsors, and structural events (mergers/splits)
- **Gentle Web Scraping**: Automated data collection from ProCyclingStats, Wikipedia, and FirstCycling

### Core Concepts

- **Managerial Node**: The persistent legal entity (e.g., "Lefevere Management")
- **Team Era**: A specific season snapshot with metadata (name, UCI code, tier, sponsors)
- **Jersey Slice**: Visual representation using sponsor color proportions
- **Lineage Event**: Structural changes (legal transfer, spiritual succession, merge, split)

## Tech Stack

- **Backend**: Python 3.11, FastAPI, PostgreSQL 15, SQLAlchemy (async)
- **Frontend**: React, Vite, D3.js
- **Infrastructure**: Docker Compose
- **Authentication**: Google OAuth + JWT

## Project Status

🚧 **In Development** - Following incremental implementation via structured prompts

## CI: Postgres-Backed Backend Tests

This repository runs a GitHub Actions job that boots Postgres 15, applies Alembic migrations, and executes the full backend test suite.

- Workflow: `.github/workflows/backend-postgres-tests.yml`
- Database URL: `postgresql+asyncpg://cycling:cycling@localhost:5432/cycling_lineage`
- Steps: checkout → install backend deps → wait for Postgres → `alembic upgrade head` → `pytest`

## Run Postgres-Backed Tests Locally

Option 1: Using Docker Compose services (backend + postgres)

```bash
docker-compose up -d postgres
cd backend
export DATABASE_URL=postgresql+asyncpg://cycling:cycling@localhost:5432/cycling_lineage
alembic upgrade head
pytest tests/ -v --tb=short
```

```powershell
docker-compose up -d postgres
Set-Location backend
$env:DATABASE_URL = "postgresql+asyncpg://cycling:cycling@localhost:5432/cycling_lineage"
alembic upgrade head
pytest tests/ -v --tb=short
```

Option 2: Makefile helper (runs Alembic migrations locally)

```bash
cd backend
export DATABASE_URL=postgresql+asyncpg://cycling:cycling@localhost:5432/cycling_lineage
make alembic-upgrade-local
pytest tests/ -v --tb=short
```

```powershell
Set-Location backend
$env:DATABASE_URL = "postgresql+asyncpg://cycling:cycling@localhost:5432/cycling_lineage"
make alembic-upgrade-local
pytest tests/ -v --tb=short
```

Notes:
- The in-memory SQLite fixtures are still used for fast unit tests; the Postgres workflow validates Alembic migrations and DB connectivity.
- The app’s `alembic/env.py` reads `DATABASE_URL` from the environment via `app.core.config.Settings`.

## Development Notes

### Async Pitfalls & Eager-Loading Strategy

The backend uses SQLAlchemy async sessions. **Critical**: Avoid lazy-loading relationships in async contexts - it causes `MissingGreenlet` errors.

**Best practices:**
- Always use `selectinload()` in repository queries to eager-load relationships
- Services should never trigger lazy-loads during serialization
- Use DTO builders (`backend/app/services/dto.py`) for consistent data shaping
- Run guard tests (`backend/tests/api/test_no_lazy_load.py`) to catch regressions

**Windows CI:**
- Tests use `python -X faulthandler -m pytest -q` to handle asyncio shutdown issues
- Post-test access violations during garbage collection are expected and don't affect results
- See `.github/workflows/python-tests.yml` for CI configuration

### Caching & Performance

**ETag Support:**
- Timeline and teams endpoints return `Cache-Control: max-age=300` and weak `ETag` headers
- Clients can send `If-None-Match` to receive `304 Not Modified` when content unchanged
- See `backend/app/core/etag.py` for ETag computation from canonical JSON

**Timeline Cache:**
- Optional in-memory cache for timeline graph (see `backend/app/core/config.py`)
- Invalidated automatically on data changes affecting timeline
- Manual invalidation: `POST /api/v1/admin/cache/invalidate`

## Getting Started

_(Instructions will be added after initial setup)_

## License
This project is licensed under the Apache License 2.0.

- See `LICENSE` for the full license text.
- See `NOTICE` for third-party attributions and notices.

## Contributing

Contributions welcome! More details coming soon.
