# ChainLines
### The ChainLines Timeline

An open-source visualization of the evolutionary history of professional cycling teams from 1900 to present.

## Overview

ChainLines is a non-commercial, open-source personal project that tracks the lineage of professional cycling teams through time, visualizing how teams evolve through rebrands, mergers, splits, and successions. The system uses a **Managerial Node** concept to represent the persistent legal entity that survives name changes.

### Key Features

- **Interactive Timeline Visualization**: Desktop D3.js "river" chart showing team evolution from 1900 to present
- **Mobile-Optimized List View**: Chronological team history optimized for mobile devices
- **Community-Driven**: Wiki-style editing with moderation system for collaborative data maintenance
- **Data Integrity**: Comprehensive tracking of team eras, sponsors, and structural events (mergers/splits)
- **Gentle Web Scraping**: Automated data collection from ProCyclingStats, Wikipedia, and FirstCycling
- **GDPR Compliance**: Self-hosted fonts, transparent data handling, German legal compliance

### Core Concepts

- **Managerial Node**: The persistent legal entity behind a team (e.g., "Lefevere Management") that survives name changes
- **Team Era**: A specific season snapshot with complete metadata (name, UCI code, tier, sponsors)
- **Jersey Slice**: Visual representation of team jerseys using sponsor color proportions
- **Lineage Event**: Structural changes that alter team identity (legal transfer, spiritual succession, merge, split)

## Tech Stack

### Backend
- **Runtime**: Python 3.11
- **Framework**: FastAPI with async/await
- **Database**: PostgreSQL 15 (asyncpg driver)
- **ORM**: SQLAlchemy 2.0 (async mode)
- **Migrations**: Alembic
- **Testing**: pytest, pytest-asyncio, httpx
- **Web Scraping**: Beautiful Soup 4
- **Authentication**: Google OAuth 2.0, python-jose (JWT)

### Frontend
- **Framework**: React 18
- **Build Tool**: Vite
- **Visualization**: D3.js v7
- **Routing**: React Router v6
- **State Management**: TanStack Query (React Query)
- **HTTP Client**: Axios
- **Authentication**: @react-oauth/google
- **Testing**: Vitest, Testing Library
- **Typography**: Montserrat (self-hosted for GDPR compliance)

### Infrastructure
- **Containerization**: Docker, Docker Compose
- **Reverse Proxy**: Caddy (automatic HTTPS)
- **Web Server**: Nginx (frontend static files)
- **CI/CD**: GitHub Actions (Python tests, Postgres integration tests)
- **Hosting**: Hetzner (German hosting provider)

## Project Status

🚧 **In Development** - Following incremental implementation via structured prompts

### 📋 Implementation Guide

The complete implementation plan is documented in `prompts/CTT_PP_CLAUDE_v2.md` - a 55-prompt structured guide covering all phases from foundation to deployment.

⚠️ **IMPORTANT**: This file is **protected and should not be modified**. It serves as the authoritative reference for the entire project implementation. Any changes require explicit owner approval via PR review.

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

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)

### Quick Start with Docker Compose

1. **Clone the repository**
   ```bash
   git clone https://github.com/fjungplan/chainlines.git
   cd chainlines
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration (database credentials, Google OAuth, etc.)
   ```

3. **Start all services**
   ```bash
   docker-compose up -d
   ```

   This starts:
   - PostgreSQL database (port 5432)
   - Backend API (port 8000, exposed via Caddy)
   - Frontend (port 80/443 via Caddy)
   - Caddy reverse proxy (automatic HTTPS)

4. **Access the application**
   - Frontend: http://localhost (or your configured domain)
   - Backend API: http://localhost/api
   - API Documentation: http://localhost/api/docs

### Local Development

#### Backend Development
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up database (requires running Postgres)
export DATABASE_URL=postgresql+asyncpg://cycling:cycling@localhost:5432/cycling_lineage
alembic upgrade head

# Run tests
pytest tests/ -v

# Start development server
uvicorn app.main:app --reload --port 8000
```

#### Frontend Development
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Run tests
npm test
```

### Environment Variables

Required variables for production deployment:

**Database:**
- `POSTGRES_USER` - PostgreSQL username
- `POSTGRES_PASSWORD` - PostgreSQL password
- `POSTGRES_DB` - Database name
- `DATABASE_URL` - Full database connection string

**Authentication:**
- `GOOGLE_CLIENT_ID` - Google OAuth client ID
- `GOOGLE_CLIENT_SECRET` - Google OAuth client secret
- `GOOGLE_REDIRECT_URI` - OAuth callback URL
- `JWT_SECRET_KEY` - Secret for JWT token signing

**Application:**
- `CORS_ORIGINS` - Allowed CORS origins (comma-separated)
- `VITE_API_URL` - Frontend API endpoint URL
- `DEBUG` - Enable debug mode (set to "false" in production)

See `.env.example` for complete configuration template.

## Architecture

### Data Model
- **Teams**: Managerial nodes (persistent legal entities)
- **Team Eras**: Season-specific team instances with metadata
- **Sponsors**: Companies/entities sponsoring teams
- **Lineage Events**: Structural changes (mergers, splits, transfers)
- **Users**: Authentication and authorization
- **Edits**: Wiki-style change tracking with moderation

### API Structure
- `/api/v1/teams` - Team and era management
- `/api/v1/timeline` - Timeline visualization data
- `/api/v1/lineage` - Lineage event operations
- `/api/v1/sponsors` - Sponsor management
- `/api/v1/auth` - Authentication endpoints
- `/api/v1/edits` - Edit proposals and moderation
- `/api/health` - Health check endpoint

### Database Migrations
Alembic migrations are located in `backend/alembic/versions/`. Key migrations:
- `002_add_team_era.py` - Team era system
- `003_add_lineage_event.py` - Lineage tracking
- `004_add_sponsors.py` - Sponsor relationships
- `005_add_users.py` - User authentication
- `006_add_edits.py` - Edit moderation system

## Testing

### Backend Tests
```bash
cd backend

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_lineage.py -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run integration tests with Postgres
docker-compose up -d postgres
export DATABASE_URL=postgresql+asyncpg://cycling:cycling@localhost:5432/cycling_lineage
alembic upgrade head
pytest tests/integration/ -v
```

### Frontend Tests
```bash
cd frontend

# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run specific test file
npm test -- auth.spec.jsx
```

### CI/CD
GitHub Actions workflows:
- `.github/workflows/python-tests.yml` - Backend unit tests (SQLite)
- `.github/workflows/backend-postgres-tests.yml` - Integration tests (PostgreSQL)

## Documentation

- `USER_GUIDE.md` - End-user documentation for the application
- `docs/GOOGLE_OAUTH_SETUP.md` - Google OAuth configuration guide
- `docs/CTT_HLD_CLAUDE.md` - High-level design document (Claude)
- `prompts/CTT_PP_CLAUDE_v2.md` - Complete implementation guide (55 prompts)
- `TEST_FIX_SUMMARY.md` - Test suite maintenance history

## Legal & Compliance

This is a **non-commercial, open-source personal project** created for educational and historical documentation purposes. It is not affiliated with any commercial entity or professional cycling organization.

### Data Privacy (GDPR/DSGVO)
- Self-hosted Montserrat fonts (no Google Fonts CDN)
- Transparent data collection and processing
- User authentication via Google OAuth (Single Sign-On)
- JWT tokens stored in browser LocalStorage
- No tracking cookies or analytics
- Full compliance with German data protection law (DSGVO)

See `frontend/src/pages/ImprintPage.jsx` for complete Impressum and Datenschutzerklärung (German legal notices).

### Open Source Licenses
This project is licensed under the **Apache License 2.0**.

- See `LICENSE` for the full license text
- See `NOTICE` for third-party attributions and license compliance details

Key dependencies:
- **Montserrat fonts** (OFL-1.1) - Self-hosted typeface
- **psycopg2-binary** (LGPL-3.0) - PostgreSQL adapter
- **Beautiful Soup 4** (MIT) - Web scraping library
- All other dependencies listed in `NOTICE`

## Contributing

Contributions are welcome! This is a community-driven project that benefits from diverse input.

### How to Contribute
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with clear commit messages
4. Add/update tests as needed
5. Ensure all tests pass (`pytest` for backend, `npm test` for frontend)
6. Update documentation if needed
7. Submit a pull request

### Contribution Guidelines
- Follow existing code style and conventions
- Write tests for new features
- Update documentation for user-facing changes
- Keep commits focused and atomic
- Reference issues in commit messages when applicable

### Code of Conduct
Be respectful, inclusive, and constructive. This is a learning project and a welcoming space for contributors of all skill levels.

## Support & Contact

- **Repository**: https://github.com/fjungplan/chainlines
- **Issues**: https://github.com/fjungplan/chainlines/issues
- **Project Owner**: fjungplan

For licensing questions or attribution clarifications, please open an issue on GitHub.

## Acknowledgments

- Historical cycling data sourced from ProCyclingStats, Wikipedia, and FirstCycling
- Inspired by the rich history of professional cycling and its complex team genealogies
- Built with open-source tools and libraries (see `NOTICE` for complete attributions)
