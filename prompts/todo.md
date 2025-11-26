# Cycling Team Lineage Timeline - Implementation Checklist

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
- [ ] **Migration**
    - [ ] Create migration `003_add_lineage_event`.
    - [ ] Define Enum: `LEGAL_TRANSFER`, `SPIRITUAL_SUCCESSION`, `MERGE`, `SPLIT`.
- [ ] **Model**
    - [ ] Create `LineageEvent` model.
    - [ ] Add logic: `is_merge()`, `is_split()`.
- [ ] **Service Layer**
    - [ ] Create `LineageService`.
    - [ ] Implement validation logic (prevent circular refs, check years).
- [ ] **Testing**: Test lineage traversal (predecessors/successors).

### Prompt 6: Sponsor Data Model
- [ ] **Migration**
    - [ ] Create migration `004_add_sponsors`.
    - [ ] Tables: `sponsor_master`, `sponsor_brand`, `team_sponsor_link`.
- [ ] **Models**
    - [ ] Implement sponsor models.
    - [ ] Add hex color validation regex.
- [ ] **Service Layer**
    - [ ] Create `SponsorService`.
    - [ ] Implement `validate_era_sponsors` (ensure prominence sums to <= 100%).
- [ ] **Testing**: Verify Jersey composition logic and prominence constraints.

---

## Phase 2: Public Read API

### Prompt 7: Basic Team Endpoints
- [ ] **Router**
    - [ ] Create `app/api/v1/teams.py`.
    - [ ] Endpoints: `GET /teams`, `GET /teams/{id}`, `GET /teams/{id}/eras`.
- [ ] **Schemas**
    - [ ] Create Pydantic models for Responses (`TeamNodeResponse`, `TeamEraResponse`).
- [ ] **Repository**
    - [ ] Implement `TeamRepository` with filtering (year, tier) and pagination.
- [ ] **Docs**: Ensure OpenAPI/Swagger shows correct schemas.

### Prompt 8: Lineage Graph Endpoint
- [ ] **Endpoint**
    - [ ] Create `GET /api/v1/timeline`.
    - [ ] Params: `start_year`, `end_year`, `include_dissolved`.
- [ ] **Service**
    - [ ] Implement `TimelineService` (optimized join query).
- [ ] **Graph Builder**
    - [ ] Create `GraphBuilder` class to transform DB models to D3 Nodes/Links.
- [ ] **Performance**: Ensure query uses `selectinload` and indexes.

### Prompt 9: Team Detail (Mobile)
- [ ] **Endpoint**
    - [ ] Create `GET /api/v1/teams/{id}/history`.
- [ ] **Logic**
    - [ ] Implement `TeamDetailService`.
    - [ ] Calculate status (`active`, `historical`, `dissolved`).
    - [ ] Determine transition types (`REBRAND`, `ACQUISITION`, `REVIVAL`).
- [ ] **Optimization**: Minimize payload size for mobile.

---

## Phase 3: Basic Frontend Shell

### Prompt 10: React Setup & Routing
- [ ] **Dependencies**: Install `react-router-dom`, `axios`, `@tanstack/react-query`, `d3`.
- [ ] **API Client**: Configure axios instance with interceptors.
- [ ] **Routing**: Setup `App.jsx` with `BrowserRouter`.
- [ ] **Pages**: Create stubs for `HomePage`, `TeamDetailPage`, `NotFoundPage`.
- [ ] **Layout**: Create responsive `Layout` component.

### Prompt 11: Loading & Error UI
- [ ] **Components**
    - [ ] Create `LoadingSpinner` and `LoadingSkeleton`.
    - [ ] Create `ErrorDisplay` and `ErrorBoundary`.
- [ ] **Hooks**: Implement `useTimeline` and `useTeamHistory` using React Query.
- [ ] **Integration**: Wrap App in `QueryClientProvider`.

---

## Phase 4: Scraper Foundation

### Prompt 12: Scraper Infrastructure
- [ ] **Structure**: Create `app/scraper/` package.
- [ ] **Rate Limiter**: Implement `RateLimiter` class (15s delay per domain).
- [ ] **Base Class**: Create `BaseScraper` with `httpx` client.
- [ ] **Scheduler**: Implement Round-robin `ScraperScheduler`.

### Prompt 13: PCS Scraper
- [ ] **Parser**: Implement `PCScraper` using BeautifulSoup.
    - [ ] Extract name, UCI code, tier, sponsors.
- [ ] **Service**: Implement `ScraperService.upsert_scraped_data`.
    - [ ] Logic to respect `is_manual_override`.
- [ ] **Admin API**: Create endpoints to start/stop/trigger scraper.
- [ ] **Testing**: Test with saved HTML fixtures.

---

## Phase 5: Desktop Visualization

### Prompt 14: D3 Setup
- [ ] **Component**: Create `TimelineGraph.jsx` with SVG container.
- [ ] **Zoom**: Implement D3 Zoom behavior.
- [ ] **Utils**: Create `validateGraphData`.
- [ ] **Responsiveness**: Create `useResponsive` hook.

### Prompt 15: Layout Algorithm
- [ ] **Calculator**: Create `LayoutCalculator` class.
    - [ ] X-Axis: Based on `founding_year`.
    - [ ] Y-Axis: Grouped by Tier level.
- [ ] **Rendering**: Render links (Bezier curves) and nodes (rectangles).
- [ ] **Styling**: Differentiate spiritual vs. legal links.

### Prompt 16: Jersey Slice Rendering
- [ ] **Renderer**: Implement `JerseyRenderer` class.
    - [ ] Generate SVG gradients based on sponsor colors/prominence.
    - [ ] Apply shadow filters.
- [ ] **Colors**: Implement `colorUtils` (hex validation, contrast).
- [ ] **Integration**: Update `TimelineGraph` to use new renderer.

### Prompt 17: Interactive Controls
- [ ] **Zoom Manager**: Create `ZoomLevelManager` (Overview vs. Detail).
- [ ] **Detail Renderer**: Implement logic to show arrows/era-segments only on zoom.
- [ ] **UI**: Create `ControlPanel` (Year range sliders, Tier checkboxes).

### Prompt 18: Tooltips
- [ ] **Component**: Create floating `Tooltip` component.
- [ ] **Builder**: Implement `TooltipBuilder` for Node and Link data.
- [ ] **Events**: detailed hover states in D3.

### Prompt 19: Search & Navigation
- [ ] **Search Bar**: Create component with fuzzy search logic.
- [ ] **Navigation**: Implement `GraphNavigation` class.
    - [ ] `focusOnNode`: Zoom and pan animation.
    - [ ] `highlightPath`: Trace lineage path.

### Prompt 20: Performance
- [ ] **Virtualization**: Implement `ViewportManager` to cull off-screen nodes.
- [ ] **Monitoring**: Add `PerformanceMonitor` for dev mode.
- [ ] **Optimization**: Implement LOD (Level of Detail) rendering strategy.

---

## Phase 6: Authentication

### Prompt 21: Backend Auth (Google + JWT)
- [ ] **Config**: Add Google Client ID/Secret settings.
- [ ] **Migration**: Add `users` and `refresh_tokens` tables.
- [ ] **Security**: Implement JWT creation/verification utils.
- [ ] **Service**: Implement `AuthService` (verify Google token, create user).
- [ ] **Endpoints**: `POST /auth/google`, `POST /auth/refresh`, `GET /me`.

### Prompt 22: Frontend Auth
- [ ] **Dependencies**: Install `@react-oauth/google`.
- [ ] **Context**: Create `AuthContext` (handle tokens, user state).
- [ ] **Interceptor**: Add Bearer token to axios requests.
- [ ] **UI**: Create `Login` page and `UserMenu` component.

---

## Phase 7: The Wizard Editor

### Prompt 23: Metadata Wizard
- [ ] **Backend**:
    - [ ] Create `edits` table migration.
    - [ ] Implement `EditService.create_metadata_edit`.
- [ ] **Frontend**:
    - [ ] Create `EditMetadataWizard` modal.
    - [ ] Implement form validation.

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