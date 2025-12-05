# Velograph - Implementation Checklist
### The Cycling Team Lineage Timeline

## Phase 0: Foundation

### Prompt 1: Project Initialization
- [x] **Project Structure**
    - [x] Create root directory with `docker-compose.yml`.
    - [x] Create `backend/` directory (FastAPI).
    - [x] Create `frontend/` directory (React + Vite).
    - [x] Create shared `.env.example`.
- [x] **Docker Configuration**
    - [x] Configure PostgreSQL 15 service (port 5432, health check, volume).
    - [x] Configure Backend service (Python 3.11, depends on Postgres).
    - [x] Configure Frontend service (Node 18, port 5173).
- [x] **Backend Setup**
    - [x] Create `requirements.txt` (fastapi, uvicorn, sqlalchemy, asyncpg, alembic, etc.).
    - [x] Create `main.py` with basic FastAPI app.
    - [x] Create `app/core/config.py` using pydantic-settings.
- [x] **Frontend Setup**
    - [x] Initialize Vite React app.
    - [x] Install `react-router-dom` and `axios`.
- [x] **Testing**
    - [x] Add `pytest.ini`.
    - [x] Write basic `test_main.py`.
- [x] **Verification**: Run `docker-compose up` and check localhost:8000/docs.

### Prompt 2: Database Connection & Health
- [x] **Database Module**
    - [x] Implement `app/db/database.py` (Async engine, sessionmaker).
    - [x] Create `get_db()` dependency.
    - [x] Create `create_tables()` function.
    - [x] Create `check_db_connection()` function.
- [x] **Health Check**
    - [x] Create `app/api/health.py` with GET `/health`.
    - [x] Return DB connection status and timestamp.
    - [x] Return 503 if database is disconnected.
- [x] **Main Updates**
    - [x] Register health router in `main.py`.
    - [x] Add CORS middleware with settings-based origins.
    - [x] Add startup event for table creation.
    - [x] Add exception handlers for validation and general errors.
- [x] **Configuration**
    - [x] Update `.env.example` with `DATABASE_URL` and `CORS_ORIGINS`.
    - [x] Config already has DATABASE_URL, DEBUG, CORS_ORIGINS.
- [x] **Testing**: 
    - [x] Created `tests/test_health.py` with 6 comprehensive tests.
    - [x] All tests pass (9/9 total including Prompt 1 tests).
    - [x] Verified `/health` returns 200 with DB status "connected".
    - [x] Verified CORS headers allow localhost:5173.
    - [x] No errors in docker-compose logs.

### Prompt 3: Database Migration System
- [x] **Alembic Setup**
    - [x] Initialize alembic (`alembic init`).
    - [x] Configure `alembic.ini` for async PostgreSQL connection.
    - [x] Configure `env.py` with async engine and model imports.
- [x] **Base Model**
    - [x] Create `app/db/base.py` with DeclarativeBase and TimestampMixin.
- [x] **Team Node Migration**
    - [x] Create migration script for `team_node` table with indexes.
    - [x] Define `TeamNode` SQLAlchemy model with UUID primary key.
    - [x] Add validation: `founding_year >= 1900`.
- [x] **CLI Helpers**
    - [x] Create Makefile with `migrate`, `migrate-rollback`, `migrate-create` commands.
- [x] **Docker Integration**
    - [x] Update docker-compose.yml to run migrations before backend starts.
- [x] **Testing**: 
    - [x] Created `tests/test_migrations.py` with 10 tests.
    - [x] Verified migration upgrade/downgrade works correctly.
    - [x] Verified table structure, indexes, and validation.

---

## Phase 1: Core Data Model

### Prompt 4: Team Era Model
- [x] **Migration**
    - [x] Create migration `002_add_team_era`.
    - [x] Add columns: `season_year`, `registered_name`, `uci_code`, `tier_level`.
- [x] **Model**
    - [x] Create `TeamEra` model with relationships.
    - [x] Add validations (UCI code format, tier level).
- [x] **Service Layer**
    - [x] Create `TeamService` with methods: `create_era`, `get_node_with_eras`.
    - [x] Implement custom exceptions (`NodeNotFound`, `DuplicateEra`).
- [x] **Testing**: Test constraint violations and cascade deletes.

### Prompt 5: Lineage Event Model
- [x] **Migration**
    - [x] Create migration `003_add_lineage_event`.
    - [x] Define Enum: `LEGAL_TRANSFER`, `SPIRITUAL_SUCCESSION`, `MERGE`, `SPLIT`.
- [x] **Model**
    - [x] Create `LineageEvent` model.
    - [x] Add logic: `is_merge()`, `is_split()`.
    - [x] Add canonicalization logic (auto-downgrade single-leg MERGE/SPLIT to LEGAL_TRANSFER).
- [x] **Service Layer**
    - [x] Create `LineageService`.
    - [x] Implement validation logic (prevent circular refs, check years).
    - [x] Implement canonicalization for structural event integrity.
- [x] **Testing**: Test lineage traversal (predecessors/successors).
- [x] **Documentation**: Added USER_GUIDE.md explaining canonicalization behavior.

### Prompt 6: Sponsor Data Model
- [x] **Migration**
    - [x] Create migration `004_add_sponsors`.
    - [x] Tables: `sponsor_master`, `sponsor_brand`, `team_sponsor_link`.
- [x] **Models**
    - [x] Implement sponsor models.
    - [x] Add hex color validation regex (model-level via `@validates`).
- [x] **Service Layer**
    - [x] Create `SponsorService`.
    - [x] Implement `validate_era_sponsors` (ensure prominence sums to <= 100%).
- [x] **Testing**: Verify Jersey composition logic and prominence constraints (unit + integration).

✅ Status: Implemented and verified. All sponsor tests pass on SQLite; Postgres CI job applies Alembic migrations and runs the full suite.

---

## Phase 2: Public Read API

### Prompt 7: Basic Team Endpoints
- [x] **Router**
    - [x] Create `app/api/v1/teams.py`.
    - [x] Endpoints: `GET /teams`, `GET /teams/{id}`, `GET /teams/{id}/eras`.
- [x] **Schemas**
    - [x] Create Pydantic models for Responses (`TeamNodeResponse`, `TeamEraResponse`).
- [x] **Repository**
    - [x] Implement `TeamRepository` with filtering (year, tier) and pagination.
- [x] **Docs**: OpenAPI shows correct schemas (via FastAPI models) and examples will follow.
- [x] **Testing**: Added `tests/api/test_teams.py`; endpoints verified with SQLite fixtures and Postgres CI.

### Prompt 8: Lineage Graph Endpoint
- [x] **Endpoint**
    - [x] Create `GET /api/v1/timeline`.
    - [x] Params: `start_year`, `end_year`, `include_dissolved`, `tier_filter`.
- [x] **Service**
    - [x] Implement `TimelineService` (optimized join query).
- [x] **Graph Builder**
    - [x] Create `GraphBuilder` class to transform DB models to D3 Nodes/Links.
- [x] **Performance**: Ensure query uses `selectinload` and indexes.
- [x] **Caching**: Implement ETag support for conditional requests (304 responses).
- [x] **Testing**: Comprehensive test suite covering filters, lazy loading, ETags, graph invariants.

### Prompt 9: Team Detail (Mobile)
- [x] **Endpoint**
    - [x] Create `GET /api/v1/teams/{id}/history`.
- [x] **Logic**
    - [x] Implement `TeamDetailService`.
    - [x] Calculate status (`active`, `historical`, `dissolved`).
    - [x] Determine transition types (`REBRAND`, `ACQUISITION`, `REVIVAL`).
- [x] **Optimization**: Minimize payload size for mobile.
- [x] **Caching**: Implement ETag support with 304 responses.
- [x] **Testing**: Tests for basic history, successor/predecessor relationships, not found cases.

---

## Phase 3: Basic Frontend Shell

### Prompt 10: React Setup & Routing
- [x] **Dependencies**: Installed `react-router-dom`, `axios`, `@tanstack/react-query`, `d3`.
- [x] **API Client**: Configured axios instance with interceptors (`src/api/client.js`).
- [x] **Routing**: Set up `App.jsx` with `BrowserRouter`, nested routes and `Layout` wrapper.
- [x] **Pages**: Created `HomePage`, `TeamDetailPage`, `NotFoundPage`.
- [x] **Layout**: Implemented responsive `Layout` component with mobile-first CSS.
✅ Completed via branches `frontend/prompt-10-react-setup` merged into `main`.

### Prompt 11: Loading & Error UI
- [x] **Components**
    - [x] Created `LoadingSpinner` and `LoadingSkeleton`.
    - [x] Created `ErrorDisplay` and `ErrorBoundary`.
- [x] **Hooks**: Implemented `useTimeline`, `useTeamHistory`, `useTeams` using React Query.
- [x] **Integration**: Wrapped App in `QueryClientProvider` (`main.jsx`) and added global error boundary.
✅ Completed via branch `frontend/prompt-11-loading-error-handling` merged into `main`; all backend tests still pass (96/96).

---

## Phase 4: Scraper Foundation

### Prompt 12: Scraper Infrastructure
- [x] **Structure**: Create `app/scraper/` package.
- [x] **Rate Limiter**: Implement `RateLimiter` class (15s delay per domain).
- [x] **Base Class**: Create `BaseScraper` with `httpx` client.
- [x] **Scheduler**: Implement Round-robin `ScraperScheduler`.

### Prompt 13: PCS Scraper
- [x] **Parser**: Implement `PCScraper` using BeautifulSoup.
    - [x] Extract name, UCI code, tier, sponsors.
- [x] **Service**: Implement `ScraperService.upsert_scraped_data`.
    - [x] Logic to respect `is_manual_override`.
- [x] **Admin API**: Create endpoints to start/stop/trigger scraper.
- [x] **Testing**: Test with saved HTML fixtures.

✅ Status: Implemented and merged via PR #11. All 138 backend tests passing.

---

## Phase 5: Desktop Visualization

### Prompt 14: D3 Setup
- [x] **Component**: Create `TimelineGraph.jsx` with SVG container.
- [x] **Zoom**: Implement D3 Zoom behavior.
- [x] **Utils**: Create `validateGraphData`.
- [x] **Responsiveness**: Create `useResponsive` hook.

✅ Status: Implemented and merged via PR #12. D3.js installed, TimelineGraph component with zoom, graph utilities (validateGraphData, getGraphBounds), visualization constants, useResponsive hook, HomePage integration with conditional rendering.

### Prompt 15: Layout Algorithm
- [x] **Calculator**: Create `LayoutCalculator` class.
    - [x] X-Axis: Based on `founding_year`.
    - [x] Y-Axis: Grouped by Tier level.
- [x] **Rendering**: Render links (Bezier curves) and nodes (rectangles).
- [x] **Styling**: Differentiate spiritual vs. legal links.

✅ Status: Implemented and merged via PR #13. LayoutCalculator with year-based X positioning, tier-based Y grouping, dynamic node widths, Bezier curve paths. Nodes render as blue rectangles, links differentiate spiritual (dashed) vs legal (solid). Comprehensive test suite created.

### Prompt 16: Jersey Slice Rendering
- [x] **Renderer**: Implement `JerseyRenderer` class.
    - [x] Generate SVG gradients based on sponsor colors/prominence.
    - [x] Apply shadow filters.
- [x] **Colors**: Implement `colorUtils` (hex validation, contrast).
- [x] **Integration**: Update `TimelineGraph` to use new renderer.

✅ Status: Implemented and merged via PR #14. Frontend tests (Vitest) added and passing for jerseyRenderer and colorUtils; timeline layout tests updated and passing. Backend GraphBuilder now includes sponsor data with validated hex colors and rank ordering.

### Prompt 17: Interactive Controls
- [x] **Zoom Manager**: Create `ZoomLevelManager` (Overview vs. Detail).
- [x] **Detail Renderer**: Implement logic to show arrows/era-segments only on zoom.
- [x] **UI**: Create `ControlPanel` (Year range sliders, Tier checkboxes).

✅ Status: Implemented on branch `feature/prompt-17`. ZoomLevelManager detects zoom level transitions at 1.2x threshold. DetailRenderer adds arrowheads and era timelines at detail zoom. ControlPanel provides year range and tier filtering with apply/reset controls. HomePage wired to update timeline query params. All tests passing (45 frontend including 23 new tests, 138 backend).

### Prompt 18: Tooltips
- [x] **Component**: Create floating `Tooltip` component.
- [x] **Builder**: Implement `TooltipBuilder` for Node and Link data.
- [x] **Events**: detailed hover states in D3.

✅ Status: Implemented on branch `feature/prompt-18`. Tooltip component and CSS added; TooltipBuilder formats node/link content with sponsors and event details; TimelineGraph integrates tooltips on node/link hover with cursor tracking and on-screen positioning. All tests passing (47 frontend including tooltip tests, 138 backend). PR merged via squash.

### Prompt 19: Search & Navigation
- [x] **Search Bar**: Create component with fuzzy search logic.
- [x] **Navigation**: Implement `GraphNavigation` class.
    - [x] `focusOnNode`: Zoom and pan animation.
    - [x] `highlightPath`: Trace lineage path.

✅ **Status**: Implemented on branch `feature/prompt-19`. SearchBar component with fuzzy search across all eras and UCI codes; GraphNavigation utility with focusOnNode (animated zoom/pan to center node with highlight pulse) and highlightPath (BFS pathfinding with sequential link highlighting); integrated into TimelineGraph with data-id attributes on nodes/links; tests cover search ranking, era matching, result selection, and navigation methods. All tests passing (70 frontend, 138 backend). PR merged via squash.

### Prompt 20: Performance
- [x] **Virtualization**: Implement `ViewportManager` to cull off-screen nodes.
- [x] **Monitoring**: Add `PerformanceMonitor` for dev mode.
- [x] **Optimization**: Implement LOD (Level of Detail) rendering strategy.

✅ Status: Implemented on branch `feature/prompt-20`. Added `ViewportManager` (viewport culling), `PerformanceMonitor` (timing and metrics logging), `OptimizedRenderer` (queue + LOD + optional canvas). Integrated into `TimelineGraph` with debounced virtualization updates during zoom/pan, and dev-mode metrics logging. Added tests for utilities and LOD behavior. All tests passing (76 frontend, 138 backend, 1 skipped).

---

## Phase 6: Authentication

### Prompt 21: Backend Auth (Google + JWT)
- [x] **Config**: Add Google Client ID/Secret settings.
- [x] **Migration**: Add `users` and `refresh_tokens` tables.
- [x] **Security**: Implement JWT creation/verification utils.
- [x] **Service**: Implement `AuthService` (verify Google token, create user).
- [x] **Endpoints**: `POST /auth/google`, `POST /auth/refresh`, `GET /me`.
- [x] **Dependencies**: Add auth packages to requirements.txt.
- [x] **Schemas**: Create auth request/response schemas.
- [x] **Dependencies**: Implement auth dependencies (get_current_user, require_admin, etc.).
- [x] **Tests**: Comprehensive service and API tests.
- [x] **Documentation**: Google Cloud setup guide and implementation summary.

✅ **Status**: Implemented on branch `feature/prompt-21-google-oauth-v2`. Complete Google OAuth backend with JWT token management. Added all auth dependencies, configured settings, created auth schemas, implemented auth endpoints and dependencies. Comprehensive test coverage for both service layer and API layer. Detailed Google Cloud setup documentation provided. All files compile successfully, app loads with 3 auth routes registered. Ready for Prompt 22 (Frontend Auth Integration).

### Prompt 22: Frontend Auth
- [x] **Dependencies**: Install `@react-oauth/google`.
- [x] **Context**: Create `AuthContext` (handle tokens, user state).
- [x] **Interceptor**: Add Bearer token to axios requests.
- [x] **UI**: Create `Login` page and `UserMenu` component.

✅ **Status**: Complete! Frontend auth fully integrated with Google OAuth. AuthContext manages JWT tokens with auto-refresh. LoginPage with Google Sign-In button. UserMenu component displays user info with role badges. All backend timezone issues fixed. Auth flow tested and working end-to-end.

---

## Phase 7: The Wizard Editor

### Prompt 23: Metadata Wizard
- [x] **Backend**:
    - [x] Create `edits` table migration.
    - [x] Implement `EditService.create_metadata_edit`.
- [x] **Frontend**:
    - [x] Create `EditMetadataWizard` modal.
    - [x] Implement form validation.

### Prompt 24: Merge Wizard
- [ ] **Backend**:
    - [ ] Implement `create_merge_edit`.
    - [ ] Logic: Close source nodes, create new node, create lineage events.
- [ ] **Frontend**:
    - [ ] Create multi-step `MergeWizard`.
    - [ ] Integrate team search for selecting source nodes.

### Prompt 25: Split Wizard
- [ ] **Backend**:
    - [ ] Implement `create_split_edit`.
    - [ ] Logic: Create multiple new nodes from one source.
- [ ] **Frontend**:
    - [ ] Create `SplitWizard` with dynamic form fields (add/remove teams).

---

## Phase 8: Moderation System

### Prompt 26: Moderation Queue
- [ ] **Backend**:
    - [ ] Create `GET /moderation/pending` and `POST /moderation/review`.
    - [ ] Implement `ModerationService` (apply edits on approval).
- [ ] **Frontend**:
    - [ ] Create `ModerationQueuePage`.
    - [ ] Create `EditReviewModal`.
    - [ ] Display stats (approved/rejected counts).

---

## Phase 9: Mobile Optimization

### Prompt 27: Mobile List View
- [ ] **Component**: Create `MobileListView`.
- [ ] **Search/Sort**: Implement client-side filtering/sorting.
- [ ] **Team Detail**: Refine `TeamDetailPage` CSS for mobile.
- [ ] **Home Integration**: Switch between Graph/List based on viewport width.

---

## Phase 10: Polish & Deployment

### Prompt 28: Optimization & Caching
- [ ] **Backend Cache**: Implement `CacheManager` (in-memory or Redis).
- [ ] **Middleware**: Add GZip compression.
- [ ] **DB**: Configure connection pooling.
- [ ] **Frontend**: Configure code splitting and lazy loading.

### Prompt 29: SEO & Metadata
- [ ] **Meta Tags**: Implement `SEO` component using `react-helmet-async`.
- [ ] **Sitemap**: Create `GET /sitemap.xml` endpoint.
- [ ] **Robots**: Add `robots.txt`.

### Prompt 30: Production Docker
- [ ] **Dockerfiles**: Create multi-stage `Dockerfile.prod` for both services.
- [ ] **Nginx**: Configure Nginx as reverse proxy and static server.
- [ ] **Gunicorn**: Configure production WSGI server.
- [ ] **Compose**: Create `docker-compose.prod.yml`.
- [ ] **Deploy Script**: Create `deploy.sh`.