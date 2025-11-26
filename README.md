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

## Getting Started

_(Instructions will be added after initial setup)_

## License
This project is licensed under the Apache License 2.0.

- See `LICENSE` for the full license text.
- See `NOTICE` for third-party attributions and notices.

## Contributing

Contributions welcome! More details coming soon.
