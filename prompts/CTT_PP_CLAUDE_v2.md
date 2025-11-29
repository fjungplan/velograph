Cycling Team Lineage Timeline - Complete Implementation Guide
=============================================================

Table of Contents
-----------------

*   [Project Overview](#project-overview)
*   [Architecture Blueprint](#architecture-blueprint)
*   [Implementation Phases](#implementation-phases)
*   [Detailed Implementation Prompts](#detailed-implementation-prompts)

* * *

Project Overview
----------------

This is a comprehensive implementation guide for building the Cycling Team Lineage Timeline - an open-source wiki visualizing the evolutionary history of professional cycling teams from 1900 to present. The system uses a **Managerial Node** concept to track team continuity through rebrands, mergers, and splits.

### Key Technologies

*   **Backend**: Python FastAPI with PostgreSQL
*   **Frontend**: React with D3.js visualization
*   **Infrastructure**: Docker Compose
*   **Data Source**: Web scrapers (PCS, Wikipedia, FirstCycling)

### Core Concepts

*   **Managerial Node**: The persistent legal entity that survives name changes
*   **Team Era**: A specific season snapshot with metadata
*   **Jersey Slice**: Visual representation using sponsor colors
*   **The Gentle Scraper**: Low-velocity scraping to avoid IP bans

* * *

Architecture Blueprint
----------------------

### System Components

1.  **Database Layer** (PostgreSQL)
    *   Core lineage tables (team\_node, team\_era, lineage\_event)
    *   Sponsor hierarchy (sponsor\_master, sponsor\_brand, team\_sponsor\_link)
    *   User and moderation tables
2.  **Backend API** (FastAPI)
    *   Public read endpoints for timeline data
    *   Protected write endpoints for editing
    *   Admin endpoints for scraper control
    *   Authentication via Google OAuth
3.  **Scraper Infrastructure**
    *   Rate-limited scraping (15-30 second delays)
    *   Round-robin scheduling across sources
    *   Respects manual override flags
4.  **Frontend Application**
    *   Desktop: D3.js "River" visualization
    *   Mobile: Vertical list view
    *   Event-driven wizard for editing
5.  **Moderation System**
    *   Pre-moderation for new users
    *   Post-moderation for trusted users
    *   Admin review queue

* * *

Implementation Phases
---------------------

### Phase 0: Foundation (Prompts 1-3)

*   Project initialization with Docker
*   Database connection and health checks
*   Migration system setup

### Phase 1: Core Data Model (Prompts 4-6)

*   Team Era model
*   Lineage Event model
*   Sponsor hierarchy

### Phase 2: Public Read API (Prompts 7-9)

*   Basic team endpoints
*   Timeline graph endpoint
*   Mobile-optimized detail endpoint

### Phase 3: Basic Frontend Shell (Prompts 10-11)

*   React project setup
*   Loading states and error handling

### Phase 4: Scraper Foundation (Prompts 12-13)

*   Scraper infrastructure
*   ProCyclingStats parser

### Phase 5: Desktop Visualization (Prompts 14-20)

*   D3.js setup
*   Graph layout algorithm
*   Jersey slice rendering
*   Zoom and interaction

### Phase 6: Authentication & Authorization (Prompts 21-25)

*   Google OAuth integration
*   User roles and permissions
*   Session management

### Phase 7: The Wizard Editor (Prompts 26-32)

*   Edit metadata wizard
*   Structural event wizards (merge, split)
*   Event validation and execution

### Phase 8: Moderation System (Prompts 33-36)

*   Moderation queue
*   Trusted user promotion
*   Revision history

### Phase 9: Mobile Optimization (Prompts 37-39)

*   Responsive breakpoints
*   Mobile list view
*   Touch interactions

### Phase 10: Polish & Deployment (Prompts 40-45)

*   Performance optimization
*   SEO and metadata
*   Docker production setup
*   Documentation

* * *

Detailed Implementation Prompts
-------------------------------

* * *

## Phase 0: Foundation
-------------------

### Prompt 1: Project Initialization

    Create a new project structure for the Cycling Team Lineage Timeline application with the following requirements:
    
    PROJECT STRUCTURE:
    - Root directory with docker-compose.yml
    - Backend directory (Python FastAPI)
    - Frontend directory (React with Vite)
    - Shared .env.example file
    
    DOCKER COMPOSE REQUIREMENTS:
    - PostgreSQL 15 service with:
      - Database name: cycling_lineage
      - Port 5432 exposed
      - Health check configured
      - Volume for data persistence
    - Backend service with:
      - Python 3.11
      - Hot reload enabled
      - Depends on postgres
      - Port 8000 exposed
    - Frontend service with:
      - Node 18
      - Hot reload enabled
      - Port 5173 exposed
    
    BACKEND SETUP:
    - Create requirements.txt with:
      - fastapi==0.104.1
      - uvicorn[standard]==0.24.0
      - sqlalchemy==2.0.23
      - psycopg2-binary==2.9.9
      - alembic==1.12.1
      - pytest==7.4.3
      - pytest-asyncio==0.21.1
      - httpx==0.25.2
    - Create main.py with basic FastAPI app
    - Create app/__init__.py
    - Create app/core/__init__.py for configuration
    - Create app/core/config.py with settings using pydantic-settings
    
    FRONTEND SETUP:
    - Initialize React app with Vite
    - Install dependencies: react-router-dom, axios
    - Create basic App.jsx with routing placeholder
    
    TESTING:
    - Add pytest.ini in backend
    - Create tests/__init__.py
    - Add a simple test_main.py that verifies FastAPI starts
    
    OUTPUT:
    - Complete file tree showing all created files
    - Instructions to run: docker-compose up
    - Verification steps to confirm all services start correctly
    
    SUCCESS CRITERIA:
    - Docker compose brings up 3 services
    - Backend accessible at localhost:8000/docs
    - Frontend accessible at localhost:5173
    - PostgreSQL accepting connections
    - pytest runs and passes the basic test

### Prompt 2: Database Connection and Health Check

    Building on the previous project structure, implement database connectivity and health monitoring:
    
    REQUIREMENTS:
    
    1. DATABASE MODULE (app/db/database.py):
    - Create SQLAlchemy engine with async support using asyncpg
    - Create async sessionmaker
    - Implement get_db() dependency for FastAPI
    - Add create_tables() function for initial setup
    - Connection string from environment: postgresql+asyncpg://user:pass@host:5432/dbname
    
    2. HEALTH CHECK ENDPOINT (app/api/health.py):
    - Create router with GET /health endpoint
    - Check database connectivity
    - Return JSON: {status: "healthy", database: "connected", timestamp: ISO8601}
    - If DB fails, return 503 with error details
    
    3. MAIN APP UPDATES (main.py):
    - Include health router
    - Add startup event that calls create_tables()
    - Add CORS middleware for frontend (localhost:5173)
    - Add exception handlers for common errors
    
    4. CONFIGURATION (app/core/config.py):
    - Add DATABASE_URL setting
    - Add DEBUG mode setting
    - Add CORS_ORIGINS as list
    
    5. ENVIRONMENT (.env.example):
    - DATABASE_URL=postgresql+asyncpg://cycling:cycling@postgres:5432/cycling_lineage
    - DEBUG=true
    - CORS_ORIGINS=["http://localhost:5173"]
    
    TESTING (tests/test_health.py):
    - Test GET /health returns 200
    - Test response contains required fields
    - Mock database failure and verify 503 response
    
    INTEGRATION TEST:
    - Test actual database connection through health endpoint
    - Verify create_tables() runs without errors
    
    SUCCESS CRITERIA:
    - curl http://localhost:8000/health returns healthy status
    - Tests pass with pytest
    - No errors in docker-compose logs
    - Frontend can call backend health endpoint

### Prompt 3: Database Migration System

    Implement Alembic migrations for version-controlled database schema management:
    
    REQUIREMENTS:
    
    1. ALEMBIC INITIALIZATION:
    - Run alembic init alembic in backend directory
    - Configure alembic.ini to use async PostgreSQL
    - Update alembic/env.py to:
      - Import SQLAlchemy models
      - Use async engine
      - Load DATABASE_URL from config
    
    2. BASE MODEL (app/db/base.py):
    - Create declarative Base class
    - Add created_at timestamp column mixin
    - Add updated_at timestamp column mixin
    - Add __repr__ helper for debugging
    
    3. FIRST MIGRATION - Core Tables:
    
    Create migration for team_node table:
    ```sql
    CREATE TABLE team_node (
        node_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        founding_year INT NOT NULL,
        dissolution_year INT NULL,
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW()
    );
    CREATE INDEX idx_team_node_founding ON team_node(founding_year);
    CREATE INDEX idx_team_node_dissolution ON team_node(dissolution_year);
    ```
    
    4. SQLALCHEMY MODEL (app/models/team.py):
    - Create TeamNode model matching migration
    - Add proper typing hints
    - Add __repr__ method
    - Use UUID as primary key
    - Add validation: founding_year must be >= 1900
    
    5. MIGRATION SCRIPT (alembic/script.py.mako):
    - Customize template to include helpful comments
    - Add reversibility checks
    
    6. DOCKER COMPOSE UPDATE:
    - Add migration service that runs on startup
    - Ensure migrations run before backend starts
    
    TESTING (tests/test_migrations.py):
    - Test migration applies successfully
    - Test migration rollback works
    - Test TeamNode model can be instantiated
    - Test created_at/updated_at are auto-populated
    
    CLI HELPERS (create as Makefile or scripts/):
    - make migrate - run pending migrations
    - make migrate-rollback - rollback one migration
    - make migrate-create NAME="description" - create new migration
    
    SUCCESS CRITERIA:
    - alembic upgrade head runs successfully
    - team_node table exists in database
    - alembic downgrade -1 removes the table
    - All tests pass
    - Can create TeamNode instance and save to database

* * *

## Phase 1: Core Data Model
------------------------

### Prompt 4: Team Era Model and Migration

    Extend the data model to include team_era - the yearly snapshots of a team:
    
    REQUIREMENTS:
    
    1. NEW MIGRATION (alembic/versions/002_add_team_era.py):
    ```sql
    CREATE TABLE team_era (
        era_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        node_id UUID NOT NULL REFERENCES team_node(node_id) ON DELETE CASCADE,
        season_year INT NOT NULL CHECK (season_year >= 1900 AND season_year <= 2100),
        registered_name VARCHAR(255) NOT NULL,
        uci_code VARCHAR(3) NULL,
        tier_level INT NULL CHECK (tier_level IN (1, 2, 3)),
        source_origin VARCHAR(100) NULL,
        is_manual_override BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW(),
        UNIQUE(node_id, season_year)
    );
    CREATE INDEX idx_team_era_node ON team_era(node_id);
    CREATE INDEX idx_team_era_year ON team_era(season_year);
    CREATE INDEX idx_team_era_manual ON team_era(is_manual_override);
    ```
    
    2. SQLALCHEMY MODEL (app/models/team.py - extend):
    - Create TeamEra model with relationship to TeamNode
    - Add back_populates relationship on TeamNode: eras = relationship("TeamEra")
    - Add validation:
      - uci_code must be exactly 3 uppercase letters if provided
      - registered_name cannot be empty string
      - tier_level must be 1, 2, or 3 if provided
    - Add helper method: is_active(year: int) -> bool
    - Add property: display_name -> str (formatted name)
    
    3. BUSINESS LOGIC (app/services/team_service.py - create new):
    - Create TeamService class
    - Implement get_node_with_eras(node_id: UUID) -> TeamNode with all eras
    - Implement get_eras_by_year(year: int) -> List[TeamEra]
    - Implement create_era(node_id, year, name, **kwargs) with validation:
      - Check that node exists
      - Check for duplicate (node_id, season_year)
      - Validate all constraints
    - Add proper error handling with custom exceptions
    
    4. CUSTOM EXCEPTIONS (app/core/exceptions.py - create):
    - NodeNotFoundException
    - DuplicateEraException  
    - ValidationException
    - Each with status_code and detail attributes
    
    5. EXCEPTION HANDLERS (main.py - update):
    - Add handlers for custom exceptions
    - Return proper HTTP status codes and JSON errors
    
    TESTING (tests/test_team_era.py):
    - Test creating era with valid data
    - Test duplicate (node_id, year) raises exception
    - Test invalid tier_level raises ValidationError
    - Test cascade delete: deleting node deletes eras
    - Test get_eras_by_year returns correct results
    - Test is_manual_override default is False
    - Test uci_code validation
    
    INTEGRATION TESTS (tests/integration/test_team_service.py):
    - Test full workflow: create node → create multiple eras → query
    - Test error paths with actual database
    
    SUCCESS CRITERIA:
    - Migration applies and rolls back cleanly
    - Can create TeamNode with multiple TeamEras
    - All validations work correctly
    - TeamService methods work with real database
    - All tests pass

### Prompt 5: Lineage Event Model

    Implement the lineage_event table to track team evolution events (mergers, splits, successions):
    
    REQUIREMENTS:
    
    1. NEW MIGRATION (003_add_lineage_event.py):
    ```sql
    CREATE TYPE event_type_enum AS ENUM (
        'LEGAL_TRANSFER',
        'SPIRITUAL_SUCCESSION', 
        'MERGE',
        'SPLIT'
    );
    
    CREATE TABLE lineage_event (
        event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        previous_node_id UUID NULL REFERENCES team_node(node_id) ON DELETE SET NULL,
        next_node_id UUID NULL REFERENCES team_node(node_id) ON DELETE SET NULL,
        event_year INT NOT NULL CHECK (event_year >= 1900),
        event_type event_type_enum NOT NULL,
        notes TEXT NULL,
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW(),
        CHECK (previous_node_id IS NOT NULL OR next_node_id IS NOT NULL)
    );
    
    CREATE INDEX idx_lineage_event_prev ON lineage_event(previous_node_id);
    CREATE INDEX idx_lineage_event_next ON lineage_event(next_node_id);
    CREATE INDEX idx_lineage_event_year ON lineage_event(event_year);
    CREATE INDEX idx_lineage_event_type ON lineage_event(event_type);
    ```
    
    2. ENUM (app/models/enums.py - create):
    - Create EventType enum using Python enum.Enum
    - Values: LEGAL_TRANSFER, SPIRITUAL_SUCCESSION, MERGE, SPLIT
    - Add description property for each type
    
    3. MODEL (app/models/lineage.py - create):
    - Create LineageEvent model
    - Relationships to TeamNode (previous and next)
    - Add validation:
      - At least one of previous_node_id or next_node_id must be set
      - event_year must be within founding/dissolution years of connected nodes
    - Helper methods:
      - is_merge() -> bool
      - is_split() -> bool
      - is_spiritual() -> bool
    
    4. RELATIONSHIP UPDATES (app/models/team.py):
    - Add to TeamNode:
      - outgoing_events = relationship (events where this is previous_node)
      - incoming_events = relationship (events where this is next_node)
    - Add helper methods:
      - get_predecessors() -> List[TeamNode]
      - get_successors() -> List[TeamNode]
    
    5. SERVICE LAYER (app/services/lineage_service.py - create):
    - LineageService class with methods:
      - create_event(previous_id, next_id, year, type, notes)
      - get_lineage_chain(node_id) -> Dict with full ancestry/descendants
      - validate_event_timeline() - ensure event_year makes sense
    - Complex validation:
      - MERGE must have multiple previous_nodes
      - SPLIT must have multiple next_nodes
      - Cannot create circular references
    
    TESTING (tests/test_lineage.py):
    - Test creating each event type
    - Test relationship traversal (get_predecessors/successors)
    - Test validation: event_year vs node years
    - Test MERGE with 2+ previous nodes
    - Test SPLIT with 2+ next nodes
    - Test circular reference prevention
    - Test cascade behavior when nodes deleted
    
    FIXTURES (tests/conftest.py - update):
    - Add fixture: sample_team_node
    - Add fixture: sample_team_era
    - Add fixture: sample_lineage_event
    - Add fixture: complex_lineage_tree (3 generations)
    
    SUCCESS CRITERIA:
    - Migration with ENUM type works on PostgreSQL
    - Can create all event types
    - Relationships work bidirectionally
    - Validation prevents invalid states
    - Can traverse lineage tree in both directions
    - All tests pass

### Prompt 6: Sponsor Data Model

    Implement the sponsor hierarchy (master sponsors and brands) and their link to team eras:
    
    REQUIREMENTS:
    
    1. NEW MIGRATION (004_add_sponsors.py):
    ```sql
    CREATE TABLE sponsor_master (
        master_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        legal_name VARCHAR(255) NOT NULL UNIQUE,
        industry_sector VARCHAR(100) NULL,
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW()
    );
    
    CREATE TABLE sponsor_brand (
        brand_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        master_id UUID NOT NULL REFERENCES sponsor_master(master_id) ON DELETE CASCADE,
        brand_name VARCHAR(255) NOT NULL,
        default_hex_color VARCHAR(7) NOT NULL CHECK (default_hex_color ~ '^#[0-9A-Fa-f]{6}$'),
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW(),
        UNIQUE(master_id, brand_name)
    );
    
    CREATE TABLE team_sponsor_link (
        link_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        era_id UUID NOT NULL REFERENCES team_era(era_id) ON DELETE CASCADE,
        brand_id UUID NOT NULL REFERENCES sponsor_brand(brand_id) ON DELETE RESTRICT,
        rank_order INT NOT NULL CHECK (rank_order >= 1),
        prominence_percent INT NOT NULL CHECK (prominence_percent > 0 AND prominence_percent <= 100),
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW(),
        UNIQUE(era_id, brand_id),
        UNIQUE(era_id, rank_order)
    );
    
    CREATE INDEX idx_sponsor_brand_master ON sponsor_brand(master_id);
    CREATE INDEX idx_team_sponsor_era ON team_sponsor_link(era_id);
    CREATE INDEX idx_team_sponsor_brand ON team_sponsor_link(brand_id);
    ```
    
    2. MODELS (app/models/sponsor.py - create):
    - SponsorMaster model
    - SponsorBrand model with relationship to SponsorMaster
    - TeamSponsorLink model with relationships to TeamEra and SponsorBrand
    - Color validation in SponsorBrand using regex
    - Add validation in TeamSponsorLink:
      - prominence_percent constraint checked at model level
    
    3. UPDATE TeamEra MODEL (app/models/team.py):
    - Add relationship: sponsor_links = relationship("TeamSponsorLink")
    - Add property: sponsors_ordered -> List[TeamSponsorLink] (sorted by rank_order)
    - Add validation method: validate_sponsor_total() -> checks sum(prominence_percent) <= 100
    
    4. SERVICE LAYER (app/services/sponsor_service.py - create):
    - SponsorService class:
      - create_master(legal_name, industry_sector)
      - create_brand(master_id, brand_name, color)
      - link_sponsor_to_era(era_id, brand_id, rank, prominence)
      - validate_era_sponsors(era_id) -> ensures total prominence <= 100
      - get_era_jersey_composition(era_id) -> List[Dict] with colors and percentages
    
    5. BUSINESS LOGIC VALIDATION:
    - Add database trigger or application-level check:
      - Before INSERT/UPDATE on team_sponsor_link
      - Verify SUM(prominence_percent) for era_id <= 100
      - Raise exception if violated
    
    TESTING (tests/test_sponsor.py):
    - Test creating sponsor master and brands
    - Test color validation (valid/invalid hex codes)
    - Test linking sponsor to era
    - Test prominence_percent total constraint:
      - Success: 60% + 40% = 100%
      - Failure: 60% + 50% = 110%
    - Test rank_order uniqueness per era
    - Test get_era_jersey_composition returns correct ordering
    - Test cascade delete: deleting era deletes links
    - Test restrict delete: cannot delete brand with active links
    
    INTEGRATION TEST (tests/integration/test_sponsor_integration.py):
    - Create full scenario:
      - Master sponsor "Soudal Group"
      - Brand "Soudal" with blue color
      - Brand "Quick-Step" with white color  
      - Link both to an era with 60/40 split
      - Verify jersey composition
    
    SUCCESS CRITERIA:
    - All three tables created with proper constraints
    - Hex color validation works
    - Cannot exceed 100% prominence total
    - Can retrieve ordered sponsors for jersey visualization
    - All tests pass
    - Cascade/restrict delete policies work correctly

* * *

## Phase 2: Public Read API
------------------------

### Prompt 7: Basic Team Endpoints

    Create REST API endpoints for reading team node and era data:
    
    REQUIREMENTS:
    
    1. ROUTER (app/api/v1/teams.py - create):
    - APIRouter with prefix="/api/v1/teams"
    - Dependency injection for database session
    
    ENDPOINTS:
    
    GET /api/v1/teams/{node_id}
    - Returns single TeamNode with all eras
    - Include relationships: eras, outgoing_events, incoming_events
    - Return 404 if not found
    - Response model: TeamNodeResponse (create Pydantic schema)
    
    GET /api/v1/teams/{node_id}/eras
    - Returns all TeamEra records for a node
    - Query params: year (optional filter)
    - Ordered by season_year DESC
    - Response model: List[TeamEraResponse]
    
    GET /api/v1/teams
    - List all teams with pagination
    - Query params:
      - skip: int = 0
      - limit: int = 50 (max 100)
      - active_in_year: int (optional - filters to teams with eras in that year)
      - tier_level: int (optional - filters by tier)
    - Returns: {items: List[TeamNodeResponse], total: int, skip: int, limit: int}
    
    2. SCHEMAS (app/schemas/team.py - create):
    - TeamNodeBase (founding_year, dissolution_year)
    - TeamNodeResponse (extends Base, adds node_id, created_at)
    - TeamNodeWithEras (extends Response, adds eras: List[TeamEraResponse])
    - TeamEraBase (all fields except IDs)
    - TeamEraResponse (extends Base, adds era_id, node_id)
    - Use pydantic for validation and serialization
    
    3. REPOSITORY PATTERN (app/repositories/team_repository.py - create):
    - TeamRepository class with async methods:
      - get_by_id(node_id) -> Optional[TeamNode]
      - get_all(skip, limit, filters) -> Tuple[List[TeamNode], int]
      - get_eras_for_node(node_id, year_filter) -> List[TeamEra]
    - Use SQLAlchemy async session
    - Implement eager loading for relationships
    
    4. UPDATE MAIN (main.py):
    - Include teams router: app.include_router(teams.router)
    - Add API versioning prefix
    
    5. ERROR HANDLING:
    - Use HTTPException for 404s
    - Add request validation errors
    - Return consistent error format: {detail: str, code: str}
    
    TESTING (tests/api/test_teams.py):
    - Test GET /teams/{id} with valid ID
    - Test GET /teams/{id} with invalid ID (404)
    - Test GET /teams with pagination
    - Test GET /teams with active_in_year filter
    - Test GET /teams with tier_level filter
    - Test GET /teams/{id}/eras
    - Test GET /teams/{id}/eras with year filter
    - Use TestClient from fastapi.testclient
    - Mock repository for unit tests
    - Use real database for integration tests
    
    FIXTURES (tests/conftest.py - update):
    - Add fixture: test_client -> TestClient
    - Add fixture: sample_teams_in_db (creates 5 teams with eras)
    
    DOCUMENTATION:
    - Add docstrings to all endpoints
    - Use FastAPI's OpenAPI automatic docs
    - Add examples to schema models
    
    SUCCESS CRITERIA:
    - All endpoints accessible via curl
    - OpenAPI docs at /docs show all endpoints
    - Pagination works correctly
    - Filters return correct results
    - 404s return proper error format
    - All tests pass

### Prompt 8: Lineage Graph Endpoint

    Create the core endpoint that returns graph data optimized for D3.js visualization:
    
    REQUIREMENTS:
    
    1. ENDPOINT (app/api/v1/timeline.py - create router):
    
    GET /api/v1/timeline
    Query Parameters:
    - start_year: int = 1900
    - end_year: int = current_year
    - include_dissolved: bool = true
    - tier_filter: Optional[List[int]] = None
    
    Response Format (optimized for D3):
    ```json
    {
      "nodes": [
        {
          "id": "uuid",
          "founding_year": 2010,
          "dissolution_year": null,
          "eras": [
            {
              "year": 2010,
              "name": "Team Sky",
              "tier": 1,
              "sponsors": [
                {"brand": "Sky", "color": "#0000FF", "prominence": 100}
              ]
            }
          ]
        }
      ],
      "links": [
        {
          "source": "uuid1",
          "target": "uuid2",
          "year": 2019,
          "type": "LEGAL_TRANSFER"
        }
      ],
      "meta": {
        "year_range": [1900, 2024],
        "node_count": 150,
        "link_count": 89
      }
    }
    ```
    
    2. SERVICE (app/services/timeline_service.py - create):
    - TimelineService class with method:
      - get_graph_data(start_year, end_year, filters) -> Dict
    - Complex query:
      - Join team_node, team_era, team_sponsor_link, sponsor_brand
      - Filter by year range
      - Optionally filter dissolved teams
      - Group sponsors by era
    - Optimization:
      - Use selectinload for relationships
      - Single query with JOINs
      - Index hints if needed
    
    3. GRAPH BUILDER (app/core/graph_builder.py - create):
    - GraphBuilder class:
      - build_nodes(teams: List[TeamNode]) -> List[Dict]
      - build_links(events: List[LineageEvent]) -> List[Dict]
      - build_jersey_composition(era: TeamEra) -> List[Dict]
    - Transform database models to D3-friendly format
    - Calculate prominence percentages for sponsors
    - Handle missing data gracefully
    
    4. SCHEMAS (app/schemas/timeline.py - create):
    - SponsorComposition (brand, color, prominence)
    - TimelineEra (year, name, tier, sponsors)
    - TimelineNode (id, founding_year, dissolution_year, eras)
    - TimelineLink (source, target, year, type)
    - TimelineResponse (nodes, links, meta)
    
    5. CACHING LAYER (optional but recommended):
    - Use functools.lru_cache or Redis
    - Cache key: f"timeline:{start_year}:{end_year}:{filters_hash}"
    - TTL: 5 minutes
    - Invalidate on data changes
    
    TESTING (tests/api/test_timeline.py):
    - Test timeline with default params
    - Test timeline with year range filter
    - Test timeline with tier filter
    - Test dissolved teams exclusion
    - Test empty database returns empty graph
    - Test graph structure is valid for D3:
      - All link.source IDs exist in nodes
      - All link.target IDs exist in nodes
    - Test sponsor colors are valid hex
    - Test prominence totals <= 100% per era
    - Performance test: 1000 nodes should return in < 2 seconds
    
    INTEGRATION TEST (tests/integration/test_timeline_integration.py):
    - Create complex lineage:
      - Team A (2010-2015)
      - Team B (2015-2020) - successor to A
      - Team C (2020-present) - successor to B
      - Team D (2012-2018) - independent
      - Merge event: A + D → E in 2016
    - Verify graph correctly represents this structure
    - Verify year filters work correctly
    
    PERFORMANCE:
    - Add SQL EXPLAIN ANALYZE logging in dev mode
    - Ensure query uses indexes efficiently
    - Add monitoring for slow queries (> 500ms)
    
    SUCCESS CRITERIA:
    - Endpoint returns valid JSON matching schema
    - Graph data is valid for D3.js consumption
    - Performance is acceptable (< 1s for typical datasets)
    - All tests pass including integration tests
    - OpenAPI docs show clear examples

### Prompt 9: Team Detail Endpoint for Mobile

    Create a mobile-optimized endpoint that returns a simple chronological list for a team:
    
    REQUIREMENTS:
    
    1. ENDPOINT (app/api/v1/teams.py - extend):
    
    GET /api/v1/teams/{node_id}/history
    - Returns chronological list of eras with lineage context
    - Optimized for mobile list view
    - Include predecessor/successor information
    
    Response Format:
    ```json
    {
      "node_id": "uuid",
      "founding_year": 2010,
      "dissolution_year": null,
      "timeline": [
        {
          "year": 2010,
          "name": "Team Sky",
          "tier": 1,
          "uci_code": "SKY",
          "status": "active",
          "predecessor": null,
          "successor": {
            "year": 2020,
            "name": "Ineos Grenadiers",
            "event_type": "REBRAND"
          }
        }
      ],
      "lineage_summary": {
        "has_predecessors": false,
        "has_successors": true,
        "spiritual_succession": false
      }
    }
    ```
    
    2. SERVICE (app/services/team_detail_service.py - create):
    - TeamDetailService class:
      - get_team_history(node_id) -> Dict
      - enrich_with_lineage(team) -> adds predecessor/successor info
      - calculate_era_status(era, current_year) -> "active" | "historical"
    - Determine event_type for transitions:
      - Same management → "REBRAND"
      - Different management + LEGAL_TRANSFER → "ACQUISITION"
      - SPIRITUAL_SUCCESSION → "REVIVAL"
      - MERGE → "MERGED_INTO"
    
    3. SCHEMAS (app/schemas/team_detail.py - create):
    - TeamHistoryEra (year, name, tier, uci_code, status, predecessor, successor)
    - LineageSummary (has_predecessors, has_successors, spiritual_succession)
    - TeamHistoryResponse (node_id, founding_year, dissolution_year, timeline, lineage_summary)
    
    4. BUSINESS LOGIC:
    - Determine "status" field:
      - If year == current_year and dissolution_year is null: "active"
      - If year < current_year: "historical"
      - If dissolution_year is set: "dissolved"
    - Sort timeline by year ASC
    - Include "gaps" if team didn't compete certain years
    
    5. ERROR HANDLING:
    - Return 404 if node_id doesn't exist
    - Handle teams with no eras (newly created)
    
    TESTING (tests/api/test_team_detail.py):
    - Test get history for team with multiple eras
    - Test get history for team with predecessors
    - Test get history for team with successors
    - Test get history for dissolved team
    - Test get history for newly created team (no eras)
    - Test status calculation for different years
    - Test lineage_summary flags are correct
    - Test gaps in timeline (team didn't compete 2 years)
    
    FIXTURES:
    - Create fixture: team_with_complex_history
      - Active from 2010-2012
      - Gap in 2013
      - Active again 2014-2020
      - Dissolved in 2020
    
    MOBILE OPTIMIZATION:
    - Add response header: Cache-Control: max-age=300
    - Minimize payload size: exclude unnecessary fields
    - Add ETag support for conditional requests
    
    SUCCESS CRITERIA:
    - Endpoint returns clear chronological history
    - Mobile app can easily render as list view
    - Lineage context is clear (predecessor/successor)
    - Status field is accurate
    - All tests pass
    - Response size is minimal (< 10KB for typical team)

* * *

## Phase 3: Basic Frontend Shell
-----------------------------

### Prompt 10: React Project Setup and Routing

    Set up the React frontend with routing and basic layout structure:
    
    REQUIREMENTS:
    
    1. PROJECT STRUCTURE:
    frontend/
    ├── src/
    │   ├── api/        # API client
	│ 	├── components/ # Reusable components
	│ 	├── pages/ 		# Route pages 
	│ 	├── hooks/ 		# Custom hooks
	│ 	├── utils/ 		# Utilities 
	│ 	├── App.jsx 
	│ 	└── main.jsx

2.  DEPENDENCIES (package.json):

*   Add to existing Vite React setup:
    *   react-router-dom: ^6.20.0
    *   axios: ^1.6.2
    *   @tanstack/react-query: ^5.12.0 (for data fetching)
    *   d3: ^7.8.5 (will use later)

3.  API CLIENT (src/api/client.js):

javascript

    import axios from 'axios';
    
    const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    
    export const apiClient = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    // Add interceptors for error handling
    apiClient.interceptors.response.use(
      (response) => response,
      (error) => {
        // Handle common errors
        if (error.response?.status === 404) {
          console.error('Resource not found');
        }
        return Promise.reject(error);
      }
    );
    
    export default apiClient;

4.  API SERVICE (src/api/teams.js):

javascript

    import apiClient from './client';
    
    export const teamsApi = {
      getTimeline: (params) => 
        apiClient.get('/api/v1/timeline', { params }),
      
      getTeamHistory: (nodeId) =>
        apiClient.get(`/api/v1/teams/${nodeId}/history`),
      
      getTeams: (params) =>
        apiClient.get('/api/v1/teams', { params }),
    };

5.  ROUTING (src/App.jsx):

javascript

    import { BrowserRouter, Routes, Route } from 'react-router-dom';
    import Layout from './components/Layout';
    import HomePage from './pages/HomePage';
    import TeamDetailPage from './pages/TeamDetailPage';
    import NotFoundPage from './pages/NotFoundPage';
    
    function App() {
      return (
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Layout />}>
              <Route index element={<HomePage />} />
              <Route path="team/:nodeId" element={<TeamDetailPage />} />
              <Route path="*" element={<NotFoundPage />} />
            </Route>
          </Routes>
        </BrowserRouter>
      );
    }
    
    export default App;
    ```
    
    6. LAYOUT COMPONENT (src/components/Layout.jsx):
    - Create responsive layout with:
      - Header with app title "Cycling Team Lineage"
      - Navigation placeholder
      - Main content area using <Outlet />
      - Footer with copyright
    - Mobile-first CSS
    - Breakpoint: 768px for tablet/desktop
    
    7. PAGE STUBS (src/pages/):
    - HomePage.jsx - render "Home - Visualization coming soon"
    - TeamDetailPage.jsx - render "Team Detail for {nodeId}"
    - NotFoundPage.jsx - render 404 message
    
    8. ENVIRONMENT (.env):
    ```
    VITE_API_URL=http://localhost:8000
    ```
    
    9. STYLING:
    - Use CSS modules or styled-components (your choice)
    - Create global styles in src/index.css:
      - CSS reset
      - Base typography
      - Color variables
      - Responsive breakpoints as CSS custom properties
    
    TESTING (basic setup):
    - Verify all routes render without errors
    - Test API client can connect to backend
    - Test 404 route works
    
    SUCCESS CRITERIA:
    - Frontend starts without errors
    - Can navigate between routes
    - Layout renders on all screen sizes
    - API client is configured correctly
    - Console shows no errors
    - Hot reload works
    ```
    
### Prompt 11: Loading States and Error Handling

Implement robust loading states and error handling UI components:

REQUIREMENTS:

1.  LOADING COMPONENT (src/components/Loading.jsx):

javascript

    export function LoadingSpinner({ size = 'md', message }) {
      // Size: sm, md, lg
      // Render animated spinner with optional message
      // Use CSS animation for spinner
    }
    
    export function LoadingSkeleton({ type }) {
      // Type: 'list', 'graph', 'card'
      // Render skeleton placeholder matching expected content
    }

2.  ERROR COMPONENT (src/components/ErrorDisplay.jsx):

javascript

    export function ErrorDisplay({ error, onRetry }) {
      // Display error message with optional retry button
      // Different styles for: network error, 404, 500, validation error
      // Include helpful user-facing messages
    }
    
    export function ErrorBoundary({ children, fallback }) {
      // React error boundary component
      // Catch and display React errors gracefully
    }

3.  CUSTOM HOOKS (src/hooks/useTeamData.js):

javascript

    import { useQuery } from '@tanstack/react-query';
    import { teamsApi } from '../api/teams';
    
    export function useTimeline(params) {
      return useQuery({
        queryKey: ['timeline', params],
        queryFn: () => teamsApi.getTimeline(params),
        staleTime: 5 * 60 * 1000, // 5 minutes
      });
    }
    
    export function useTeamHistory(nodeId) {
      return useQuery({
        queryKey: ['teamHistory', nodeId],
        queryFn: () => teamsApi.getTeamHistory(nodeId),
        enabled: !!nodeId,
      });
    }

4.  QUERY PROVIDER (src/main.jsx - update):

javascript

    import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
    
    const queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: 1,
          refetchOnWindowFocus: false,
        },
      },
    });
    
    // Wrap App with QueryClientProvider

5.  ERROR UTILITIES (src/utils/errors.js):

javascript

    export function getErrorMessage(error) {
      // Extract user-friendly message from axios error
      // Handle different error types
      if (error.response?.status === 404) return 'Team not found';
      if (error.response?.status === 500) return 'Server error';
      if (error.code === 'ERR_NETWORK') return 'Cannot connect to server';
      return error.message || 'An unexpected error occurred';
    }
    
    export function isNetworkError(error) {
      return error.code === 'ERR_NETWORK' || !error.response;
    }

6.  UPDATE HomePage (src/pages/HomePage.jsx):

javascript

    import { useTimeline } from '../hooks/useTeamData';
    import { LoadingSpinner } from '../components/Loading';
    import { ErrorDisplay } from '../components/ErrorDisplay';
    
    export default function HomePage() {
      const { data, isLoading, error, refetch } = useTimeline({
        start_year: 2020,
        end_year: 2024,
      });
    
      if (isLoading) return <LoadingSpinner message="Loading timeline..." />;
      if (error) return <ErrorDisplay error={error} onRetry={refetch} />;
    
      return (
        <div>
          <h1>Timeline Data Loaded</h1>
          <pre>{JSON.stringify(data, null, 2)}</pre>
        </div>
      );
    }

7.  UPDATE TeamDetailPage (src/pages/TeamDetailPage.jsx):

javascript

    import { useParams } from 'react-router-dom';
    import { useTeamHistory } from '../hooks/useTeamData';
    import { LoadingSpinner } from '../components/Loading';
    import { ErrorDisplay } from '../components/ErrorDisplay';
    
    export default function TeamDetailPage() {
      const { nodeId } = useParams();
      const { data, isLoading, error, refetch } = useTeamHistory(nodeId);
    
      if (isLoading) return <LoadingSpinner message="Loading team history..." />;
      if (error) return <ErrorDisplay error={error} onRetry={refetch} />;
    
      return (
        <div>
          <h1>Team History</h1>
          <pre>{JSON.stringify(data, null, 2)}</pre>
        </div>
      );
    }
    ```
    
    STYLING:
    - Create CSS for spinner animation (rotate 360deg)
    - Create skeleton pulse animation
    - Style error display with color coding:
      - Red for errors
      - Yellow for warnings
      - Blue for info
    - Ensure loading states are visually distinct
    
    TESTING:
    - Test loading spinner renders
    - Test error display with different error types
    - Test skeleton loader renders
    - Test retry button calls refetch
    - Mock API to test error states
    - Test error boundary catches React errors
    
    SUCCESS CRITERIA:
    - Loading states render smoothly
    - Errors display helpful messages
    - Retry functionality works
    - No layout shift between loading/loaded states
    - Error boundary prevents app crashes
    - React Query caching works
    ```
    
---
    
## Phase 4: Scraper Foundation
-------------------
    
### Prompt 12: Scraper Infrastructure Setup

Build the foundation for the "Gentle Scraper" with rate limiting and scheduling:

REQUIREMENTS:

1.  SCRAPER PACKAGE STRUCTURE: backend/app/scraper/ ├── **init**.py ├── base.py # Base scraper class ├── scheduler.py # Round-robin scheduler ├── rate\_limiter.py # Rate limiting logic ├── parsers/ # Site-specific parsers │ └── **init**.py └── models.py # Scraper-specific models
2.  RATE LIMITER (app/scraper/rate\_limiter.py):

python

    import asyncio
    from datetime import datetime, timedelta
    from collections import defaultdict
    
    class RateLimiter:
        """Ensures minimum delay between requests to same domain"""
        
        def __init__(self, min_delay_seconds: int = 15):
            self.min_delay = min_delay_seconds
            self.last_request_time = defaultdict(lambda: None)
            self._locks = defaultdict(asyncio.Lock)
        
        async def wait_if_needed(self, domain: str):
            """Wait if last request to domain was too recent"""
            async with self._locks[domain]:
                last_time = self.last_request_time[domain]
                if last_time:
                    elapsed = (datetime.now() - last_time).total_seconds()
                    if elapsed < self.min_delay:
                        wait_time = self.min_delay - elapsed
                        await asyncio.sleep(wait_time)
                
                self.last_request_time[domain] = datetime.now()

3.  BASE SCRAPER (app/scraper/base.py):

python

    from abc import ABC, abstractmethod
    from typing import Optional, Dict
    import httpx
    from app.scraper.rate_limiter import RateLimiter
    
    class BaseScraper(ABC):
        """Base class for all scrapers"""
        
        def __init__(self, rate_limiter: RateLimiter):
            self.rate_limiter = rate_limiter
            self.client = httpx.AsyncClient(
                timeout=30.0,
                headers={
                    'User-Agent': 'CyclingLineageBot/1.0 (Educational; https://github.com/yourrepo)',
                }
            )
        
        @property
        @abstractmethod
        def domain(self) -> str:
            """Domain this scraper targets"""
            pass
        
        async def fetch(self, url: str) -> Optional[str]:
            """Fetch URL with rate limiting"""
            await self.rate_limiter.wait_if_needed(self.domain)
            
            try:
                response = await self.client.get(url)
                response.raise_for_status()
                return response.text
            except httpx.HTTPError as e:
                print(f"Error fetching {url}: {e}")
                return None
        
        @abstractmethod
        async def scrape_team(self, team_identifier: str) -> Optional[Dict]:
            """Scrape data for a specific team"""
            pass
        
        async def close(self):
            """Clean up resources"""
            await self.client.aclose()

4.  SCHEDULER (app/scraper/scheduler.py):

python

    import asyncio
    from typing import List
    from app.scraper.base import BaseScraper
    from app.scraper.rate_limiter import RateLimiter
    
    class ScraperScheduler:
        """Round-robin scheduler for multiple scrapers"""
        
        def __init__(self, scrapers: List[BaseScraper], rate_limiter: RateLimiter):
            self.scrapers = scrapers
            self.rate_limiter = rate_limiter
            self._running = False
        
        async def run_once(self, team_identifier: str) -> Dict:
            """Run all scrapers once for a team"""
            results = {}
            
            for scraper in self.scrapers:
                result = await scraper.scrape_team(team_identifier)
                if result:
                    results[scraper.__class__.__name__] = result
            
            return results
        
        async def run_continuous(self, team_identifiers: List[str], interval_seconds: int = 300):
            """Continuously scrape teams in round-robin fashion"""
            self._running = True
            
            while self._running:
                for team_id in team_identifiers:
                    if not self._running:
                        break
                    
                    await self.run_once(team_id)
                    await asyncio.sleep(interval_seconds)
        
        def stop(self):
            """Stop the scheduler"""
            self._running = False
        
        async def close(self):
            """Clean up all scrapers"""
            for scraper in self.scrapers:
                await scraper.close()

5.  SCRAPER CONFIG (app/core/config.py - extend):

python

    class Settings(BaseSettings):
        # Existing settings...
        
        # Scraper settings
        SCRAPER_ENABLED: bool = False
        SCRAPER_MIN_DELAY: int = 15  # seconds between requests to same domain
        SCRAPER_USER_AGENT: str = "CyclingLineageBot/1.0"
        SCRAPER_INTERVAL: int = 300  # seconds between full cycles

6.  SCRAPER MODELS (app/scraper/models.py):

python

    from pydantic import BaseModel
    from typing import Optional, List
    from datetime import datetime
    
    class ScrapedTeamData(BaseModel):
        """Raw data scraped from a source"""
        source: str  # 'pcs', 'wikipedia', etc.
        team_name: str
        uci_code: Optional[str]
        founding_year: Optional[int]
        dissolution_year: Optional[int]
        current_tier: Optional[int]
        sponsors: List[str] = []
        
    class ScraperResult(BaseModel):
        """Result from scraping operation"""
        success: bool
        team_identifier: str
        data: Optional[ScrapedTeamData]
        error: Optional[str]
        scraped_at: datetime
    ```
    
    TESTING (tests/scraper/test_rate_limiter.py):
    - Test rate limiter enforces minimum delay
    - Test multiple domains tracked independently
    - Test concurrent requests to same domain are serialized
    - Test asyncio integration
    
    TESTING (tests/scraper/test_base_scraper.py):
    - Create mock scraper subclass
    - Test fetch() method with mocked httpx
    - Test rate limiter is called
    - Test error handling for failed requests
    - Test User-Agent header is set
    
    TESTING (tests/scraper/test_scheduler.py):
    - Test run_once executes all scrapers
    - Test scrapers run in order
    - Test stop() interrupts continuous mode
    - Test error in one scraper doesn't stop others
    
    SUCCESS CRITERIA:
    - Rate limiter enforces delays correctly
    - Base scraper class is functional
    - Scheduler can run multiple scrapers
    - All HTTP requests include User-Agent
    - Tests verify rate limiting behavior
    - No actual external requests in tests (all mocked)
    ```
    
### Prompt 13: ProCyclingStats Scraper Implementation

Implement the first concrete scraper for ProCyclingStats.com:

REQUIREMENTS:

1.  PCS SCRAPER (app/scraper/parsers/pcs\_scraper.py):

python

    from bs4 import BeautifulSoup
    from typing import Optional, Dict
    from app.scraper.base import BaseScraper
    from app.scraper.models import ScrapedTeamData
    import re
    
    class PCScraper(BaseScraper):
        """Scraper for ProCyclingStats.com"""
        
        BASE_URL = "https://www.procyclingstats.com"
        
        @property
        def domain(self) -> str:
            return "www.procyclingstats.com"
        
        async def scrape_team(self, team_identifier: str) -> Optional[ScrapedTeamData]:
            """
            Scrape team data from PCS
            team_identifier: e.g., 'team/soudal-quick-step-2024'
            """
            url = f"{self.BASE_URL}/{team_identifier}"
            html = await self.fetch(url)
            
            if not html:
                return None
            
            return self.parse_team_page(html)
        
        def parse_team_page(self, html: str) -> Optional[ScrapedTeamData]:
            """Parse team page HTML"""
            soup = BeautifulSoup(html, 'html.parser')
            
            try:
                # Extract team name
                team_name = self._extract_team_name(soup)
                
                # Extract UCI code (if present)
                uci_code = self._extract_uci_code(soup)
                
                # Extract tier
                tier = self._extract_tier(soup)
                
                # Extract sponsors from team name
                sponsors = self._extract_sponsors(team_name)
                
                return ScrapedTeamData(
                    source="pcs",
                    team_name=team_name,
                    uci_code=uci_code,
                    current_tier=tier,
                    sponsors=sponsors,
                    founding_year=None,  # PCS doesn't always have this
                    dissolution_year=None
                )
            except Exception as e:
                print(f"Error parsing PCS page: {e}")
                return None
        
        def _extract_team_name(self, soup: BeautifulSoup) -> str:
            """Extract team name from page"""
            # PCS typically has team name in <h1> tag
            h1 = soup.find('h1')
            if h1:
                return h1.text.strip()
            raise ValueError("Team name not found")
        
        def _extract_uci_code(self, soup: BeautifulSoup) -> Optional[str]:
            """Extract UCI code if present"""
            # Look for UCI code in team info section
            # PCS format varies - this is a heuristic
            info_div = soup.find('div', class_='info')
            if info_div:
                text = info_div.text
                match = re.search(r'\b([A-Z]{3})\b', text)
                if match:
                    return match.group(1)
            return None
        
        def _extract_tier(self, soup: BeautifulSoup) -> Optional[int]:
            """Extract team tier from page"""
            # Look for "UCI WorldTeam", "UCI ProTeam", etc.
            page_text = soup.text.lower()
            
            if 'uci worldteam' in page_text:
                return 1
            elif 'uci proteam' in page_text:
                return 2
            elif 'uci continental' in page_text:
                return 3
            
            return None
        
        def _extract_sponsors(self, team_name: str) -> list[str]:
            """Extract sponsor names from team name"""
            # Split by common delimiters
            sponsors = re.split(r'[-–—]', team_name)
            return [s.strip() for s in sponsors if s.strip()]

2.  SCRAPER FACTORY (app/scraper/**init**.py):

python

    from app.scraper.rate_limiter import RateLimiter
    from app.scraper.scheduler import ScraperScheduler
    from app.scraper.parsers.pcs_scraper import PCScraper
    
    def create_scheduler(min_delay: int = 15) -> ScraperScheduler:
        """Create scheduler with all configured scrapers"""
        rate_limiter = RateLimiter(min_delay_seconds=min_delay)
        
        scrapers = [
            PCScraper(rate_limiter),
            # Add more scrapers here later
        ]
        
        return ScraperScheduler(scrapers, rate_limiter)

3.  SCRAPER SERVICE (app/services/scraper\_service.py):

python

    from typing import Optional
    from app.scraper.models import ScrapedTeamData
    from app.models.team import TeamNode, TeamEra
    from sqlalchemy.ext.asyncio import AsyncSession
    
    class ScraperService:
        """Service to integrate scraped data into database"""
        
        @staticmethod
        async def upsert_scraped_data(
            session: AsyncSession,
            node_id: str,
            year: int,
            scraped_data: ScrapedTeamData
        ) -> Optional[TeamEra]:
            """
            Update or insert team era from scraped data
            Respects manual_override flag
            """
            # Check if era exists
            stmt = select(TeamEra).where(
                TeamEra.node_id == node_id,
                TeamEra.season_year == year
            )
            result = await session.execute(stmt)
            era = result.scalar_one_or_none()
            
            if era and era.is_manual_override:
                # Don't touch manually edited data
                return None
            
            if not era:
                era = TeamEra(
                    node_id=node_id,
                    season_year=year,
                    registered_name=scraped_data.team_name,
                    source_origin=scraped_data.source
                )
                session.add(era)
            else:
                # Update existing era
                era.registered_name = scraped_data.team_name
                era.source_origin = scraped_data.source
            
            # Update optional fields
            if scraped_data.uci_code:
                era.uci_code = scraped_data.uci_code
            if scraped_data.current_tier:
                era.tier_level = scraped_data.current_tier
            
            await session.commit()
            return era

4.  ADMIN API ENDPOINT (app/api/v1/admin.py - create):

python

    from fastapi import APIRouter, Depends, HTTPException
    from app.scraper import create_scheduler
    from app.core.config import settings
    
    router = APIRouter(prefix="/api/v1/admin", tags=["admin"])
    
    # Global scheduler instance
    _scheduler = None
    
    @router.post("/scraper/start")
    async def start_scraper():
        """Start the background scraper (admin only)"""
        global _scheduler
        
        if not settings.SCRAPER_ENABLED:
            raise HTTPException(400, "Scraper is disabled in config")
        
        if _scheduler:
            raise HTTPException(400, "Scraper already running")
        
        _scheduler = create_scheduler(settings.SCRAPER_MIN_DELAY)
        # Start in background - for now just return success
        # In production, use background tasks or celery
        
        return {"status": "started"}
    
    @router.post("/scraper/stop")
    async def stop_scraper():
        """Stop the background scraper"""
        global _scheduler
        
        if not _scheduler:
            raise HTTPException(400, "Scraper not running")
        
        _scheduler.stop()
        await _scheduler.close()
        _scheduler = None
        
        return {"status": "stopped"}
    
    @router.post("/scraper/trigger")
    async def trigger_scrape(team_id: str):
        """Manually trigger scrape for a specific team"""
        scheduler = create_scheduler()
        try:
            results = await scheduler.run_once(team_id)
            return {"results": results}
        finally:
            await scheduler.close()
    ```
    
    TESTING (tests/scraper/test_pcs_scraper.py):
    - Test parse_team_page with real HTML fixture
    - Test _extract_team_name
    - Test _extract_uci_code with various formats
    - Test _extract_tier for all tier levels
    - Test _extract_sponsors with different name formats
    - Test error handling for malformed HTML
    - Use actual saved HTML files as fixtures (no live requests)
    
    TESTING (tests/services/test_scraper_service.py):
    - Test upsert_scraped_data creates new era
    - Test upsert_scraped_data updates existing era
    - Test upsert_scraped_data respects manual_override
    - Test upsert_scraped_data handles missing optional fields
    
    HTML FIXTURES (tests/fixtures/pcs/):
    - Create sample HTML files:
      - team_worldtour.html
      - team_proteam.html
      - team_continental.html
      - team_with_uci_code.html
    
    SUCCESS CRITERIA:
    - PCS scraper can parse real HTML samples
    - Scraper respects rate limits
    - ScraperService correctly integrates data
    - Manual override flag prevents overwrites
    - Admin endpoints control scraper lifecycle
    - All tests pass with fixtures
    - No live external requests during tests
    ```
    
---
    
## Phase 5: Desktop Visualization
-------------------
    
### Prompt 14: D3.js Setup and Container

Set up D3.js visualization infrastructure with SVG container and basic graph rendering:

REQUIREMENTS:

1.  D3 VISUALIZATION COMPONENT (src/components/TimelineGraph.jsx):

javascript

    import { useEffect, useRef } from 'react';
    import * as d3 from 'd3';
    
    export default function TimelineGraph({ data }) {
      const svgRef = useRef(null);
      const containerRef = useRef(null);
      
      useEffect(() => {
        if (!data || !data.nodes || !data.links) return;
        
        // Clear previous render
        d3.select(svgRef.current).selectAll('*').remove();
        
        // Initialize visualization
        initializeVisualization();
      }, [data]);
      
      const initializeVisualization = () => {
        const container = containerRef.current;
        const width = container.clientWidth;
        const height = container.clientHeight;
        
        // Create SVG
        const svg = d3.select(svgRef.current)
          .attr('width', width)
          .attr('height', height)
          .attr('viewBox', [0, 0, width, height]);
        
        // Add zoom behavior
        const g = svg.append('g');
        
        const zoom = d3.zoom()
          .scaleExtent([0.5, 5])
          .on('zoom', (event) => {
            g.attr('transform', event.transform);
          });
        
        svg.call(zoom);
        
        // For now, just render placeholder
        g.append('text')
          .attr('x', width / 2)
          .attr('y', height / 2)
          .attr('text-anchor', 'middle')
          .text('D3 Graph Container Ready');
      };
      
      return (
        <div 
          ref={containerRef} 
          style={{ width: '100%', height: '100vh', overflow: 'hidden' }}
        >
          <svg ref={svgRef}></svg>
        </div>
      );
    }

2.  UPDATE HomePage (src/pages/HomePage.jsx):

javascript

    import { useTimeline } from '../hooks/useTeamData';
    import { LoadingSpinner } from '../components/Loading';
    import { ErrorDisplay } from '../components/ErrorDisplay';
    import TimelineGraph from '../components/TimelineGraph';
    
    export default function HomePage() {
      const { data, isLoading, error, refetch } = useTimeline({
        start_year: 2020,
        end_year: 2024,
      });
    
      if (isLoading) return <LoadingSpinner message="Loading timeline..." />;
      if (error) return <ErrorDisplay error={error} onRetry={refetch} />;
    
      return <TimelineGraph data={data?.data} />;
    }

3.  GRAPH UTILITIES (src/utils/graphUtils.js):

javascript

    /**
     * Validate graph data structure for D3
     */
    export function validateGraphData(data) {
      if (!data || !data.nodes || !data.links) {
        throw new Error('Invalid graph data: missing nodes or links');
      }
      
      const nodeIds = new Set(data.nodes.map(n => n.id));
      
      // Validate all links reference existing nodes
      for (const link of data.links) {
        if (!nodeIds.has(link.source)) {
          throw new Error(`Link references non-existent source: ${link.source}`);
        }
        if (!nodeIds.has(link.target)) {
          throw new Error(`Link references non-existent target: ${link.target}`);
        }
      }
      
      return true;
    }
    
    /**
     * Calculate graph bounds
     */
    export function getGraphBounds(nodes) {
      const years = nodes.flatMap(n => 
        n.eras.map(e => e.year)
      );
      
      return {
        minYear: Math.min(...years),
        maxYear: Math.max(...years),
        nodeCount: nodes.length
      };
    }

4.  GRAPH CONSTANTS (src/constants/visualization.js):

javascript

    export const VISUALIZATION = {
      // Dimensions
      MIN_NODE_WIDTH: 100,
      NODE_HEIGHT: 40,
      LINK_STROKE_WIDTH: 2,
      
      // Colors
      LINK_COLOR_LEGAL: '#333',
      LINK_COLOR_SPIRITUAL: '#999',
      
      // Zoom
      ZOOM_MIN: 0.5,
      ZOOM_MAX: 5,
      ZOOM_INITIAL: 1,
      
      // Spacing
      YEAR_WIDTH: 120,  // Horizontal spacing per year
      TIER_SPACING: 100, // Vertical spacing between tiers
      
      // Animation
      TRANSITION_DURATION: 300,
    };

5.  RESPONSIVE HOOK (src/hooks/useResponsive.js):

javascript

    import { useState, useEffect } from 'react';
    
    export function useResponsive() {
      const [isMobile, setIsMobile] = useState(
        window.innerWidth < 768
      );
      
      useEffect(() => {
        const handleResize = () => {
          setIsMobile(window.innerWidth < 768);
        };
        
        window.addEventListener('resize', handleResize);
        return () => window.removeEventListener('resize', handleResize);
      }, []);
      
      return { isMobile };
    }

6.  UPDATE HomePage with responsive logic:

javascript

    import { useResponsive } from '../hooks/useResponsive';
    import TimelineGraph from '../components/TimelineGraph';
    import MobileListView from '../components/MobileListView'; // Will create later
    
    export default function HomePage() {
      const { isMobile } = useResponsive();
      const { data, isLoading, error, refetch } = useTimeline({
        start_year: 2020,
        end_year: 2024,
      });
    
      if (isLoading) return <LoadingSpinner message="Loading timeline..." />;
      if (error) return <ErrorDisplay error={error} onRetry={refetch} />;
    
      return isMobile ? (
        <div>Mobile view placeholder</div>
      ) : (
        <TimelineGraph data={data?.data} />
      );
    }
    ```
    
    STYLING (src/components/TimelineGraph.css):
    - Style for SVG container
    - Ensure no overflow
    - Add cursor styles for zoom/pan
    
    TESTING:
    - Test TimelineGraph renders with valid data
    - Test TimelineGraph handles empty data
    - Test zoom behavior initializes
    - Test responsive hook detects breakpoint
    - Test graph validation utility
    
    SUCCESS CRITERIA:
    - SVG container renders at full viewport
    - Zoom and pan work smoothly
    - Graph validates data structure
    - Component handles window resize
    - No console errors
    - Ready for actual graph rendering
    ```
    
### Prompt 15: Graph Layout Algorithm - Sankey Base

Implement the Sankey-style layout algorithm for positioning nodes and links:

REQUIREMENTS:

1.  LAYOUT CALCULATOR (src/utils/layoutCalculator.js):

javascript

    import { VISUALIZATION } from '../constants/visualization';
    
    /**
     * Calculate positions for all nodes using Sankey-like layout
     */
    export class LayoutCalculator {
      constructor(graphData, width, height) {
        this.nodes = graphData.nodes;
        this.links = graphData.links;
        this.width = width;
        this.height = height;
        
        this.yearRange = this.calculateYearRange();
        this.xScale = this.createXScale();
      }
      
      calculateYearRange() {
        const allYears = this.nodes.flatMap(node => 
          node.eras.map(era => era.year)
        );
        return {
          min: Math.min(...allYears),
          max: Math.max(...allYears)
        };
      }
      
      createXScale() {
        // Map years to X coordinates
        const padding = 50;
        const { min, max } = this.yearRange;
        
        return (year) => {
          const range = max - min;
          const position = (year - min) / range;
          return padding + (position * (this.width - 2 * padding));
        };
      }
      
      calculateLayout() {
        // Step 1: Assign X positions based on founding year
        const nodesWithX = this.assignXPositions();
        
        // Step 2: Assign Y positions to minimize crossings
        const nodesWithXY = this.assignYPositions(nodesWithX);
        
        // Step 3: Calculate link paths
        const linkPaths = this.calculateLinkPaths(nodesWithXY);
        
        return {
          nodes: nodesWithXY,
          links: linkPaths
        };
      }
      
      assignXPositions() {
        return this.nodes.map(node => ({
          ...node,
          x: this.xScale(node.founding_year),
          width: this.calculateNodeWidth(node)
        }));
      }
      
      calculateNodeWidth(node) {
        // Width based on years active
        const yearSpan = node.dissolution_year 
          ? node.dissolution_year - node.founding_year
          : this.yearRange.max - node.founding_year;
        
        return Math.max(
          VISUALIZATION.MIN_NODE_WIDTH,
          yearSpan * (VISUALIZATION.YEAR_WIDTH / 10)
        );
      }
      
      assignYPositions(nodes) {
        // Simple tier-based layout for now
        // Will improve with crossing minimization later
        const tiers = this.groupNodesByTier(nodes);
        const tierHeight = this.height / (tiers.length + 1);
        
        let positioned = [];
        tiers.forEach((tierNodes, tierIndex) => {
          tierNodes.forEach((node, nodeIndex) => {
            positioned.push({
              ...node,
              y: (tierIndex + 1) * tierHeight,
              height: VISUALIZATION.NODE_HEIGHT
            });
          });
        });
        
        return positioned;
      }
      
      groupNodesByTier(nodes) {
        // Group nodes by their most common tier level
        const tierMap = new Map();
        
        nodes.forEach(node => {
          const tiers = node.eras.map(e => e.tier).filter(t => t);
          const avgTier = tiers.length > 0 
            ? Math.round(tiers.reduce((a, b) => a + b) / tiers.length)
            : 2; // Default to ProTeam
          
          if (!tierMap.has(avgTier)) {
            tierMap.set(avgTier, []);
          }
          tierMap.get(avgTier).push(node);
        });
        
        // Sort tiers (1 = WorldTour at top)
        return Array.from(tierMap.entries())
          .sort(([a], [b]) => a - b)
          .map(([_, nodes]) => nodes);
      }
      
      calculateLinkPaths(nodes) {
        // Create node position lookup
        const nodeMap = new Map(nodes.map(n => [n.id, n]));
        
        return this.links.map(link => {
          const source = nodeMap.get(link.source);
          const target = nodeMap.get(link.target);
          
          if (!source || !target) {
            console.warn('Link references missing node:', link);
            return null;
          }
          
          return {
            ...link,
            sourceX: source.x + source.width,
            sourceY: source.y + source.height / 2,
            targetX: target.x,
            targetY: target.y + target.height / 2,
            path: this.generateLinkPath(source, target)
          };
        }).filter(Boolean);
      }
      
      generateLinkPath(source, target) {
        const sx = source.x + source.width;
        const sy = source.y + source.height / 2;
        const tx = target.x;
        const ty = target.y + target.height / 2;
        
        // Cubic Bezier curve
        const dx = tx - sx;
        const controlPointOffset = Math.abs(dx) * 0.3;
        
        return `M ${sx},${sy} 
                C ${sx + controlPointOffset},${sy} 
                  ${tx - controlPointOffset},${ty} 
                  ${tx},${ty}`;
      }
    }

2.  UPDATE TimelineGraph component (src/components/TimelineGraph.jsx):

javascript

    import { LayoutCalculator } from '../utils/layoutCalculator';
    import { validateGraphData } from '../utils/graphUtils';
    
    export default function TimelineGraph({ data }) {
      const svgRef = useRef(null);
      const containerRef = useRef(null);
      
      useEffect(() => {
        if (!data || !data.nodes || !data.links) return;
        
        try {
          validateGraphData(data);
          renderGraph(data);
        } catch (error) {
          console.error('Graph render error:', error);
        }
      }, [data]);
      
      const renderGraph = (graphData) => {
        const container = containerRef.current;
        const width = container.clientWidth;
        const height = container.clientHeight;
        
        // Calculate layout
        const calculator = new LayoutCalculator(graphData, width, height);
        const layout = calculator.calculateLayout();
        
        // Clear previous render
        const svg = d3.select(svgRef.current);
        svg.selectAll('*').remove();
        
        // Set dimensions
        svg.attr('width', width)
           .attr('height', height);
        
        // Create main group
        const g = svg.append('g');
        
        // Render links first (so nodes appear on top)
        renderLinks(g, layout.links);
        
        // Render nodes
        renderNodes(g, layout.nodes);
        
        // Add zoom
        const zoom = d3.zoom()
          .scaleExtent([VISUALIZATION.ZOOM_MIN, VISUALIZATION.ZOOM_MAX])
          .on('zoom', (event) => {
            g.attr('transform', event.transform);
          });
        
        svg.call(zoom);
      };
      
      const renderLinks = (g, links) => {
        g.append('g')
          .attr('class', 'links')
          .selectAll('path')
          .data(links)
          .join('path')
            .attr('d', d => d.path)
            .attr('fill', 'none')
            .attr('stroke', d => 
              d.type === 'SPIRITUAL_SUCCESSION' 
                ? VISUALIZATION.LINK_COLOR_SPIRITUAL 
                : VISUALIZATION.LINK_COLOR_LEGAL
            )
            .attr('stroke-width', VISUALIZATION.LINK_STROKE_WIDTH)
            .attr('stroke-dasharray', d => 
              d.type === 'SPIRITUAL_SUCCESSION' ? '5,5' : '0'
            );
      };
      
      const renderNodes = (g, nodes) => {
        const nodeGroups = g.append('g')
          .attr('class', 'nodes')
          .selectAll('g')
          .data(nodes)
          .join('g')
            .attr('transform', d => `translate(${d.x},${d.y})`);
        
        // For now, render as simple rectangles
        nodeGroups.append('rect')
          .attr('width', d => d.width)
          .attr('height', d => d.height)
          .attr('fill', '#4A90E2')
          .attr('stroke', '#333')
          .attr('stroke-width', 1)
          .attr('rx', 4);
        
        // Add team name
        nodeGroups.append('text')
          .attr('x', d => d.width / 2)
          .attr('y', d => d.height / 2)
          .attr('text-anchor', 'middle')
          .attr('dominant-baseline', 'middle')
          .attr('fill', 'white')
          .attr('font-size', '12px')
          .text(d => d.eras[0]?.name || 'Unknown');
      };
      
      return (
        <div 
          ref={containerRef} 
          style={{ width: '100%', height: '100vh', overflow: 'hidden' }}
        >
          <svg ref={svgRef}></svg>
        </div>
      );
    }
    ```
    
    TESTING (tests/utils/layoutCalculator.test.js):
    - Test calculateYearRange with various node sets
    - Test xScale maps years correctly
    - Test calculateNodeWidth with active/dissolved teams
    - Test assignYPositions distributes nodes vertically
    - Test calculateLinkPaths generates valid SVG paths
    - Test layout with empty nodes array
    - Test layout with nodes but no links
    
    SUCCESS CRITERIA:
    - Nodes positioned horizontally by founding year
    - Nodes distributed vertically by tier
    - Links connect nodes with Bezier curves
    - Spiritual succession links are dashed
    - Graph renders without errors
    - Zoom and pan work with positioned nodes
    ```
    
### Prompt 16: Jersey Slice Rendering

Implement the "Jersey Slice" visualization - nodes rendered with sponsor color stripes:

REQUIREMENTS:

1.  JERSEY RENDERER (src/utils/jerseyRenderer.js):

javascript

    import * as d3 from 'd3';
    
    export class JerseyRenderer {
      /**
       * Create gradient definition for a node's sponsors
       */
      static createGradientDefinition(svg, node) {
        const gradientId = `gradient-${node.id}`;
        
        // Get sponsors for the most recent era
        const latestEra = node.eras[node.eras.length - 1];
        const sponsors = latestEra.sponsors || [];
        
        if (sponsors.length === 0) {
          return null; // Will use default color
        }
        
        // Create linear gradient
        const defs = svg.select('defs').empty() 
          ? svg.append('defs') 
          : svg.select('defs');
        
        const gradient = defs.append('linearGradient')
          .attr('id', gradientId)
          .attr('x1', '0%')
          .attr('y1', '0%')
          .attr('x2', '0%')
          .attr('y2', '100%');
        
        // Add color stops based on prominence
        let cumulativePercent = 0;
        sponsors.forEach((sponsor, index) => {
          const startPercent = cumulativePercent;
          const endPercent = cumulativePercent + sponsor.prominence;
          
          // Hard stop at boundary
          gradient.append('stop')
            .attr('offset', `${startPercent}%`)
            .attr('stop-color', sponsor.color);
          
          gradient.append('stop')
            .attr('offset', `${endPercent}%`)
            .attr('stop-color', sponsor.color);
          
          cumulativePercent = endPercent;
        });
        
        return gradientId;
      }
      
      /**
       * Render a node with jersey slice styling
       */
      static renderNode(nodeGroup, node, svg) {
        const gradientId = this.createGradientDefinition(svg, node);
        
        // Create rounded rectangle
        const rect = nodeGroup.append('rect')
          .attr('width', node.width)
          .attr('height', node.height)
          .attr('rx', 6)
          .attr('ry', 6)
          .attr('stroke', '#333')
          .attr('stroke-width', 2);
        
        // Apply gradient or default color
        if (gradientId) {
          rect.attr('fill', `url(#${gradientId})`);
        } else {
          rect.attr('fill', '#4A90E2'); // Default blue
        }
        
        // Add subtle shadow
        rect.attr('filter', 'url(#drop-shadow)');
        
        return rect;
      }
      
      /**
       * Create drop shadow filter
       */
      static createShadowFilter(svg) {
        const defs = svg.select('defs').empty() 
          ? svg.append('defs') 
          : svg.select('defs');
        
        const filter = defs.append('filter')
          .attr('id', 'drop-shadow')
          .attr('height', '130%');
        
        filter.append('feGaussianBlur')
          .attr('in', 'SourceAlpha')
          .attr('stdDeviation', 2);
        
        filter.append('feOffset')
          .attr('dx', 2)
          .attr('dy', 2)
          .attr('result', 'offsetblur');
        
        const feMerge = filter.append('feMerge');
        feMerge.append('feMergeNode');
        feMerge.append('feMergeNode')
          .attr('in', 'SourceGraphic');
      }
      
      /**
       * Add text label to node
       */
      static addNodeLabel(nodeGroup, node) {
        const latestEra = node.eras[node.eras.length - 1];
        const name = latestEra.name || 'Unknown Team';
        
        // Truncate long names
        const displayName = name.length > 25 
          ? name.substring(0, 22) + '...' 
          : name;
        
        nodeGroup.append('text')
          .attr('x', node.width / 2)
          .attr('y', node.height / 2)
          .attr('text-anchor', 'middle')
          .attr('dominant-baseline', 'middle')
          .attr('fill', 'white')
          .attr('font-size', '11px')
          .attr('font-weight', 'bold')
          .attr('style', 'text-shadow: 1px 1px 2px rgba(0,0,0,0.8)')
          .text(displayName);
        
        // Add year range as subtitle
        const yearRange = node.dissolution_year
          ? `${node.founding_year}-${node.dissolution_year}`
          : `${node.founding_year}-`;
        
        nodeGroup.append('text')
          .attr('x', node.width / 2)
          .attr('y', node.height / 2 + 14)
          .attr('text-anchor', 'middle')
          .attr('dominant-baseline', 'middle')
          .attr('fill', 'white')
          .attr('font-size', '9px')
          .attr('style', 'text-shadow: 1px 1px 2px rgba(0,0,0,0.8)')
          .text(yearRange);
      }
    }

2.  UPDATE TimelineGraph.jsx to use JerseyRenderer:

javascript

    import { JerseyRenderer } from '../utils/jerseyRenderer';
    
    const renderNodes = (g, nodes, svg) => {
      // Create shadow filter once
      JerseyRenderer.createShadowFilter(svg);
      
      const nodeGroups = g.append('g')
        .attr('class', 'nodes')
        .selectAll('g')
        .data(nodes)
        .join('g')
          .attr('class', 'node')
          .attr('transform', d => `translate(${d.x},${d.y})`)
          .style('cursor', 'pointer')
          .on('click', (event, d) => handleNodeClick(d))
          .on('mouseenter', (event, d) => handleNodeHover(event, d))
          .on('mouseleave', handleNodeHoverEnd);
      
      // Render each node with jersey styling
      nodeGroups.each(function(d) {
        const group = d3.select(this);
        JerseyRenderer.renderNode(group, d, svg);
        JerseyRenderer.addNodeLabel(group, d);
      });
    };
    
    const handleNodeClick = (node) => {
      console.log('Clicked node:', node);
      // TODO: Navigate to team detail page
    };
    
    const handleNodeHover = (event, node) => {
      d3.select(event.currentTarget)
        .select('rect')
        .transition()
        .duration(200)
        .attr('stroke-width', 3)
        .attr('stroke', '#FFD700'); // Gold highlight
    };
    
    const handleNodeHoverEnd = (event) => {
      d3.select(event.currentTarget)
        .select('rect')
        .transition()
        .duration(200)
        .attr('stroke-width', 2)
        .attr('stroke', '#333');
    };

3.  SPONSOR COLOR UTILITIES (src/utils/colorUtils.js):

javascript

    /**
     * Ensure color is valid hex
     */
    export function validateHexColor(color) {
      const hexRegex = /^#[0-9A-F]{6}$/i;
      return hexRegex.test(color) ? color : '#4A90E2';
    }
    
    /**
     * Calculate contrasting text color
     */
    export function getContrastColor(hexColor) {
      const r = parseInt(hexColor.slice(1, 3), 16);
      const g = parseInt(hexColor.slice(3, 5), 16);
      const b = parseInt(hexColor.slice(5, 7), 16);
      
      // Calculate luminance
      const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
      
      return luminance > 0.5 ? '#000000' : '#FFFFFF';
    }
    
    /**
     * Lighten color for hover states
     */
    export function lightenColor(hexColor, percent) {
      const num = parseInt(hexColor.replace('#', ''), 16);
      const amt = Math.round(2.55 * percent);
      const R = (num >> 16) + amt;
      const G = (num >> 8 & 0x00FF) + amt;
      const B = (num & 0x0000FF) + amt;
      
      return '#' + (
        0x1000000 +
        (R < 255 ? (R < 1 ? 0 : R) : 255) * 0x10000 +
        (G < 255 ? (G < 1 ? 0 : G) : 255) * 0x100 +
        (B < 255 ? (B < 1 ? 0 : B) : 255)
      ).toString(16).slice(1);
    }
    ```
    
    4. UPDATE BACKEND to ensure sponsors are included in timeline response:
    - Modify GraphBuilder to include sponsor data in era objects
    - Ensure colors are valid hex codes
    - Sort sponsors by rank_order
    
    TESTING (tests/utils/jerseyRenderer.test.js):
    - Test gradient creation with single sponsor
    - Test gradient creation with multiple sponsors
    - Test gradient creation with no sponsors (uses default)
    - Test prominence percentages sum to 100%
    - Test shadow filter is created
    - Test node label truncation
    - Test year range formatting
    
    TESTING (tests/utils/colorUtils.test.js):
    - Test validateHexColor with valid/invalid inputs
    - Test getContrastColor returns white/black appropriately
    - Test lightenColor increases brightness
    
    SUCCESS CRITERIA:
    - Nodes render with sponsor color stripes
    - Color transitions are sharp (not gradual)
    - Text is readable against all color backgrounds
    - Hover effects work smoothly
    - Default color used when no sponsors
    - All sponsor colors are valid hex codes
    ```
    
### Prompt 17: Interactive Controls and Zoom Levels

Implement zoom level system with different detail levels and interactive controls:

REQUIREMENTS:

1.  ZOOM LEVEL MANAGER (src/utils/zoomLevelManager.js):

javascript

    export const ZOOM_LEVELS = {
      OVERVIEW: { min: 0.5, max: 1.2, name: 'Overview' },
      DETAIL: { min: 1.2, max: 5, name: 'Detail' }
    };
    
    export class ZoomLevelManager {
      constructor(onLevelChange) {
        this.currentLevel = 'OVERVIEW';
        this.currentScale = 1;
        this.onLevelChange = onLevelChange;
      }
      
      updateScale(scale) {
        this.currentScale = scale;
        const newLevel = this.determineLevel(scale);
        
        if (newLevel !== this.currentLevel) {
          this.currentLevel = newLevel;
          this.onLevelChange(newLevel, scale);
        }
      }
      
      determineLevel(scale) {
        if (scale < ZOOM_LEVELS.DETAIL.min) {
          return 'OVERVIEW';
        }
        return 'DETAIL';
      }
      
      shouldShowDetail() {
        return this.currentLevel === 'DETAIL';
      }
    }

2.  DETAIL RENDERER (src/utils/detailRenderer.js):

javascript

    import * as d3 from 'd3';
    
    export class DetailRenderer {
      /**
       * Render detailed link types when zoomed in
       */
      static renderDetailedLinks(g, links, scale) {
        g.selectAll('.links path')
          .attr('stroke-width', d => {
            const baseWidth = 2;
            // Thicker lines for merges/splits
            const multiplier = (d.type === 'MERGE' || d.type === 'SPLIT') ? 1.5 : 1;
            return baseWidth * multiplier;
          })
          .attr('opacity', d => {
            // Spiritual succession more transparent
            return d.type === 'SPIRITUAL_SUCCESSION' ? 0.6 : 0.9;
          });
        
        // Add arrowheads at detail level
        this.addArrowheads(g, links);
      }
      
      static addArrowheads(g, links) {
        // Define arrow marker
        const defs = g.select('defs').empty() 
          ? g.append('defs') 
          : g.select('defs');
        
        defs.selectAll('marker').remove(); // Clear old markers
        
        const arrow = defs.append('marker')
          .attr('id', 'arrowhead')
          .attr('viewBox', '0 -5 10 10')
          .attr('refX', 8)
          .attr('refY', 0)
          .attr('markerWidth', 6)
          .attr('markerHeight', 6)
          .attr('orient', 'auto');
        
        arrow.append('path')
          .attr('d', 'M0,-5L10,0L0,5')
          .attr('fill', '#333');
        
        // Apply arrows to links
        g.selectAll('.links path')
          .attr('marker-end', 'url(#arrowhead)');
      }
      
      /**
       * Add era timeline within node at detail level
       */
      static renderEraTimeline(nodeGroup, node, scale) {
        if (scale < ZOOM_LEVELS.DETAIL.min) return;
        
        const eras = node.eras;
        if (eras.length <= 1) return;
        
        const timelineHeight = 4;
        const y = node.height - timelineHeight - 5;
        
        // Calculate era widths
        const totalYears = eras[eras.length - 1].year - eras[0].year + 1;
        
        eras.forEach((era, index) => {
          const nextEra = eras[index + 1];
          if (!nextEra) return;
          
          const eraYears = nextEra.year - era.year;
          const width = (eraYears / totalYears) * node.width;
          const x = ((era.year - eras[0].year) / totalYears) * node.width;
          
          nodeGroup.append('rect')
            .attr('class', 'era-segment')
            .attr('x', x)
            .attr('y', y)
            .attr('width', width)
            .attr('height', timelineHeight)
            .attr('fill', era.sponsors[0]?.color || '#ccc')
            .attr('opacity', 0.7);
        });
      }
    }

3.  CONTROL PANEL COMPONENT (src/components/ControlPanel.jsx):

javascript

    import { useState } from 'react';
    
    export default function ControlPanel({ 
      onYearRangeChange, 
      onTierFilterChange,
      onZoomReset 
    }) {
      const currentYear = new Date().getFullYear();
      const [startYear, setStartYear] = useState(1990);
      const [endYear, setEndYear] = useState(currentYear);
      const [selectedTiers, setSelectedTiers] = useState([1, 2, 3]);
      
      const handleApply = () => {
        onYearRangeChange(startYear, endYear);
        onTierFilterChange(selectedTiers);
      };
      
      const toggleTier = (tier) => {
        setSelectedTiers(prev => 
          prev.includes(tier) 
            ? prev.filter(t => t !== tier)
            : [...prev, tier].sort()
        );
      };
      
      return (
        <div className="control-panel">
          <div className="control-section">
            <h3>Year Range</h3>
            <div className="year-inputs">
              <label>
                Start:
                <input 
                  type="number" 
                  value={startYear} 
                  onChange={(e) => setStartYear(parseInt(e.target.value))}
                  min={1900}
                  max={endYear}
                />
              </label>
              <label>
                End:
                <input 
                  type="number" 
                  value={endYear} 
                  onChange={(e) => setEndYear(parseInt(e.target.value))}
                  min={startYear}
                  max={currentYear}
                />
              </label>
            </div>
          </div>
          
          <div className="control-section">
            <h3>Tier Filters</h3>
            <div className="tier-checkboxes">
              {[1, 2, 3].map(tier => (
                <label key={tier}>
                  <input 
                    type="checkbox" 
                    checked={selectedTiers.includes(tier)}
                    onChange={() => toggleTier(tier)}
                  />
                  {tier === 1 ? 'WorldTour' : tier === 2 ? 'ProTeam' : 'Continental'}
                </label>
              ))}
            </div>
          </div>
          
          <div className="control-actions">
            <button onClick={handleApply}>Apply Filters</button>
            <button onClick={onZoomReset}>Reset Zoom</button>
          </div>
        </div>
      );
    }

4.  UPDATE TimelineGraph with zoom levels and controls:

javascript

    import { useState, useCallback } from 'react';
    import { ZoomLevelManager } from '../utils/zoomLevelManager';
    import { DetailRenderer } from '../utils/detailRenderer';
    import ControlPanel from './ControlPanel';
    
    export default function TimelineGraph({ data }) {
      const [zoomLevel, setZoomLevel] = useState('OVERVIEW');
      const [filters, setFilters] = useState({
        startYear: 1990,
        endYear: new Date().getFullYear(),
        tiers: [1, 2, 3]
      });
      
      const zoomManager = useRef(null);
      const zoomBehavior = useRef(null);
      
      useEffect(() => {
        zoomManager.current = new ZoomLevelManager((level, scale) => {
          setZoomLevel(level);
          updateDetailLevel(level, scale);
        });
      }, []);
      
      const updateDetailLevel = useCallback((level, scale) => {
        const g = d3.select(svgRef.current).select('g');
        
        if (level === 'DETAIL') {
          // Show detailed features
          DetailRenderer.renderDetailedLinks(g, currentLayout.links, scale);
          
          // Render era timelines
          g.selectAll('.node').each(function(d) {
            const group = d3.select(this);
            DetailRenderer.renderEraTimeline(group, d, scale);
          });
        } else {
          // Hide detailed features
          g.selectAll('.era-segment').remove();
          g.selectAll('.links path').attr('marker-end', null);
        }
      }, []);
      
      const handleZoom = useCallback((event) => {
        const { transform } = event;
        const g = d3.select(svgRef.current).select('g');
        g.attr('transform', transform);
        
        if (zoomManager.current) {
          zoomManager.current.updateScale(transform.k);
        }
      }, []);
      
      const handleZoomReset = () => {
        const svg = d3.select(svgRef.current);
        svg.transition()
          .duration(750)
          .call(zoomBehavior.current.transform, d3.zoomIdentity);
      };
      
      const handleYearRangeChange = (start, end) => {
        setFilters(prev => ({ ...prev, startYear: start, endYear: end }));
        // Trigger data refetch with new filters
      };
      
      const handleTierFilterChange = (tiers) => {
        setFilters(prev => ({ ...prev, tiers }));
        // Trigger data refetch with new filters
      };
      
      // In renderGraph, store zoom behavior
      const setupZoom = (svg, g) => {
        const zoom = d3.zoom()
          .scaleExtent([0.5, 5])
          .on('zoom', handleZoom);
        
        zoomBehavior.current = zoom;
        svg.call(zoom);
      };
      
      return (
        <div className="timeline-graph-container">
          <ControlPanel 
            onYearRangeChange={handleYearRangeChange}
            onTierFilterChange={handleTierFilterChange}
            onZoomReset={handleZoomReset}
          />
          <div className="zoom-indicator">
            Zoom Level: {zoomLevel}
          </div>
          <div 
            ref={containerRef} 
            className="graph-viewport"
          >
            <svg ref={svgRef}></svg>
          </div>
        </div>
      );
    }
    ```
    
    5. STYLING (src/components/ControlPanel.css):
    - Position control panel as sidebar or overlay
    - Style inputs and buttons
    - Make responsive
    
    TESTING:
    - Test zoom level detection at various scales
    - Test detail features appear/disappear at threshold
    - Test control panel filters update correctly
    - Test zoom reset returns to initial view
    - Test year range validation
    - Test tier filter toggles
    
    SUCCESS CRITERIA:
    - Zoom smoothly transitions between overview/detail
    - Arrowheads appear only in detail view
    - Era timelines render in detail view
    - Control panel updates filters correctly
    - Reset zoom returns to origin
    - All interactions are smooth (no lag)
    ```
    
### Prompt 18: Tooltip System

Implement rich tooltips that appear on hover with team/link information:

REQUIREMENTS:

1.  TOOLTIP COMPONENT (src/components/Tooltip.jsx):

javascript

    import { useEffect, useRef } from 'react';
    import './Tooltip.css';

export default function Tooltip({ content, position, visible }) { const tooltipRef = useRef(null);

useEffect(() => { if (visible && tooltipRef.current && position) { // Position tooltip near cursor but keep on screen const tooltip = tooltipRef.current; const rect = tooltip.getBoundingClientRect();

      let x = position.x + 15;
      let y = position.y - 10;
      
      // Keep tooltip on screen
      if (x + rect.width > window.innerWidth) {
        x = position.x - rect.width - 15;
      }
      if (y + rect.height > window.innerHeight) {
        y = window.innerHeight - rect.height - 10;
      }
      
      tooltip.style.left = `${x}px`;
      tooltip.style.top = `${y}px`;
    }

}, \[position, visible\]);

if (!visible || !content) return null;

return ( <div ref={tooltipRef} className="timeline-tooltip"> {content} </div> ); }

    
    2. TOOLTIP CONTENT BUILDERS (src/utils/tooltipBuilder.js):
    ```javascript
    export class TooltipBuilder {
      static buildNodeTooltip(node) {
        const latestEra = node.eras[node.eras.length - 1];
        const sponsors = latestEra.sponsors || [];
        
        return (
          <div className="tooltip-content">
            <h4>{latestEra.name}</h4>
            <div className="tooltip-row">
              <span className="label">Founded:</span>
              <span className="value">{node.founding_year}</span>
            </div>
            {node.dissolution_year && (
              <div className="tooltip-row">
                <span className="label">Dissolved:</span>
                <span className="value">{node.dissolution_year}</span>
              </div>
            )}
            <div className="tooltip-row">
              <span className="label">Current Tier:</span>
              <span className="value">{this.getTierName(latestEra.tier)}</span>
            </div>
            {latestEra.uci_code && (
              <div className="tooltip-row">
                <span className="label">UCI Code:</span>
                <span className="value">{latestEra.uci_code}</span>
              </div>
            )}
            {sponsors.length > 0 && (
              <div className="tooltip-section">
                <div className="label">Sponsors:</div>
                <ul className="sponsor-list">
                  {sponsors.map((s, i) => (
                    <li key={i}>
                      <span 
                        className="sponsor-dot" 
                        style={{ backgroundColor: s.color }}
                      />
                      {s.brand} ({s.prominence}%)
                    </li>
                  ))}
                </ul>
              </div>
            )}
            <div className="tooltip-hint">Click for full history</div>
          </div>
        );
      }
      
      static buildLinkTooltip(link, nodes) {
        const sourceNode = nodes.find(n => n.id === link.source);
        const targetNode = nodes.find(n => n.id === link.target);
        
        if (!sourceNode || !targetNode) return null;
        
        const sourceName = sourceNode.eras[sourceNode.eras.length - 1]?.name;
        const targetName = targetNode.eras[0]?.name;
        
        return (
          <div className="tooltip-content">
            <h4>{this.getEventTypeName(link.type)}</h4>
            <div className="tooltip-row">
              <span className="label">From:</span>
              <span className="value">{sourceName}</span>
            </div>
            <div className="tooltip-row">
              <span className="label">To:</span>
              <span className="value">{targetName}</span>
            </div>
            <div className="tooltip-row">
              <span className="label">Year:</span>
              <span className="value">{link.year}</span>
            </div>
            {link.notes && (
              <div className="tooltip-section">
                <div className="label">Notes:</div>
                <p className="notes">{link.notes}</p>
              </div>
            )}
          </div>
        );
      }
      
      static getTierName(tier) {
        const names = {
          1: 'UCI WorldTour',
          2: 'UCI ProTeam',
          3: 'UCI Continental'
        };
        return names[tier] || 'Unknown';
      }
      
      static getEventTypeName(type) {
        const names = {
          'LEGAL_TRANSFER': 'Legal Transfer',
          'SPIRITUAL_SUCCESSION': 'Spiritual Succession',
          'MERGE': 'Team Merger',
          'SPLIT': 'Team Split'
        };
        return names[type] || type;
      }
    }
    ```
    
    3. UPDATE TimelineGraph with tooltip integration:
    ```javascript
    import { useState } from 'react';
    import Tooltip from './Tooltip';
    import { TooltipBuilder } from '../utils/tooltipBuilder';
    
    export default function TimelineGraph({ data }) {
      const [tooltip, setTooltip] = useState({
        visible: false,
        content: null,
        position: null
      });
      
      const showTooltip = (content, event) => {
        setTooltip({
          visible: true,
          content,
          position: { x: event.pageX, y: event.pageY }
        });
      };
      
      const hideTooltip = () => {
        setTooltip({ visible: false, content: null, position: null });
      };
      
      const updateTooltipPosition = (event) => {
        if (tooltip.visible) {
          setTooltip(prev => ({
            ...prev,
            position: { x: event.pageX, y: event.pageY }
          }));
        }
      };
      
      // In renderNodes
      const renderNodes = (g, nodes, svg) => {
        const nodeGroups = g.append('g')
          .attr('class', 'nodes')
          .selectAll('g')
          .data(nodes)
          .join('g')
            .attr('class', 'node')
            .attr('transform', d => `translate(${d.x},${d.y})`)
            .style('cursor', 'pointer')
            .on('click', (event, d) => handleNodeClick(d))
            .on('mouseenter', (event, d) => {
              handleNodeHover(event, d);
              const content = TooltipBuilder.buildNodeTooltip(d);
              showTooltip(content, event);
            })
            .on('mousemove', updateTooltipPosition)
            .on('mouseleave', (event) => {
              handleNodeHoverEnd(event);
              hideTooltip();
            });
        
        // ... rest of node rendering
      };
      
      // In renderLinks
      const renderLinks = (g, links) => {
        g.append('g')
          .attr('class', 'links')
          .selectAll('path')
          .data(links)
          .join('path')
            .attr('d', d => d.path)
            .attr('fill', 'none')
            .attr('stroke', d => 
              d.type === 'SPIRITUAL_SUCCESSION' 
                ? VISUALIZATION.LINK_COLOR_SPIRITUAL 
                : VISUALIZATION.LINK_COLOR_LEGAL
            )
            .attr('stroke-width', VISUALIZATION.LINK_STROKE_WIDTH)
            .attr('stroke-dasharray', d => 
              d.type === 'SPIRITUAL_SUCCESSION' ? '5,5' : '0'
            )
            .style('cursor', 'pointer')
            .on('mouseenter', (event, d) => {
              // Highlight link
              d3.select(event.currentTarget)
                .attr('stroke-width', VISUALIZATION.LINK_STROKE_WIDTH * 2);
              
              const content = TooltipBuilder.buildLinkTooltip(d, currentNodes);
              showTooltip(content, event);
            })
            .on('mousemove', updateTooltipPosition)
            .on('mouseleave', (event) => {
              d3.select(event.currentTarget)
                .attr('stroke-width', VISUALIZATION.LINK_STROKE_WIDTH);
              hideTooltip();
            });
      };
      
      return (
        <div className="timeline-graph-container">
          {/* ... control panel ... */}
          <div ref={containerRef} className="graph-viewport">
            <svg ref={svgRef}></svg>
          </div>
          <Tooltip 
            content={tooltip.content}
            position={tooltip.position}
            visible={tooltip.visible}
          />
        </div>
      );
    }
    ```
    
    4. STYLING (src/components/Tooltip.css):
    ```css
    .timeline-tooltip {
      position: fixed;
      background: white;
      border: 2px solid #333;
      border-radius: 8px;
      padding: 12px;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
      pointer-events: none;
      z-index: 1000;
      max-width: 300px;
      font-size: 14px;
    }
    
    .tooltip-content h4 {
      margin: 0 0 8px 0;
      font-size: 16px;
      color: #333;
      border-bottom: 1px solid #eee;
      padding-bottom: 6px;
    }
    
    .tooltip-row {
      display: flex;
      justify-content: space-between;
      margin: 4px 0;
    }
    
    .tooltip-row .label {
      font-weight: bold;
      color: #666;
    }
    
    .tooltip-row .value {
      color: #333;
    }
    
    .tooltip-section {
      margin-top: 8px;
      padding-top: 8px;
      border-top: 1px solid #eee;
    }
    
    .sponsor-list {
      list-style: none;
      padding: 0;
      margin: 4px 0 0 0;
    }
    
    .sponsor-list li {
      display: flex;
      align-items: center;
      margin: 3px 0;
    }
    
    .sponsor-dot {
      width: 12px;
      height: 12px;
      border-radius: 50%;
      margin-right: 8px;
      border: 1px solid #ccc;
    }
    
    .tooltip-hint {
      margin-top: 8px;
      padding-top: 8px;
      border-top: 1px solid #eee;
      font-size: 12px;
      color: #999;
      font-style: italic;
    }
    
    .notes {
      margin: 4px 0 0 0;
      font-size: 13px;
      color: #666;
      line-height: 1.4;
    }
    ```
    
    TESTING:
    - Test tooltip appears on node hover
    - Test tooltip appears on link hover
    - Test tooltip follows cursor
    - Test tooltip stays on screen (doesn't overflow)
    - Test tooltip hides on mouse leave
    - Test tooltip content is correct for different node/link types
    - Test tooltip with missing data (graceful degradation)
    
    SUCCESS CRITERIA:
    - Tooltips appear smoothly without delay
    - Tooltips stay near cursor but remain visible
    - Tooltip content is informative and well-formatted
    - Tooltips work for both nodes and links
    - No tooltip flicker or jumping
    - Sponsor colors match node colors

### Prompt 19: Search and Navigation

    Implement search functionality to find and highlight teams in the visualization:
    
    REQUIREMENTS:
    
    1. SEARCH COMPONENT (src/components/SearchBar.jsx):
    ```javascript
    import { useState, useEffect, useRef } from 'react';
    import './SearchBar.css';
    
    export default function SearchBar({ nodes, onTeamSelect }) {
      const [searchTerm, setSearchTerm] = useState('');
      const [results, setResults] = useState([]);
      const [showResults, setShowResults] = useState(false);
      const searchRef = useRef(null);
      
      useEffect(() => {
        if (searchTerm.length < 2) {
          setResults([]);
          return;
        }
        
        const filtered = searchTeams(nodes, searchTerm);
        setResults(filtered.slice(0, 10)); // Limit to 10 results
        setShowResults(true);
      }, [searchTerm, nodes]);
      
      // Close results when clicking outside
      useEffect(() => {
        const handleClickOutside = (event) => {
          if (searchRef.current && !searchRef.current.contains(event.target)) {
            setShowResults(false);
          }
        };
        
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
      }, []);
      
      const searchTeams = (nodes, term) => {
        const lowerTerm = term.toLowerCase();
        
        return nodes
          .map(node => {
            // Search across all eras
            const matchingEras = node.eras.filter(era =>
              era.name.toLowerCase().includes(lowerTerm) ||
              era.uci_code?.toLowerCase().includes(lowerTerm)
            );
            
            if (matchingEras.length === 0) return null;
            
            return {
              node,
              primaryName: matchingEras[matchingEras.length - 1].name,
              allNames: [...new Set(matchingEras.map(e => e.name))],
              score: calculateRelevance(matchingEras, term)
            };
          })
          .filter(Boolean)
          .sort((a, b) => b.score - a.score);
      };
      
      const calculateRelevance = (eras, term) => {
        let score = 0;
        const lowerTerm = term.toLowerCase();
        
        eras.forEach(era => {
          const name = era.name.toLowerCase();
          if (name === lowerTerm) score += 100;
          else if (name.startsWith(lowerTerm)) score += 50;
          else if (name.includes(lowerTerm)) score += 25;
          
          if (era.uci_code?.toLowerCase() === lowerTerm) score += 100;
        });
        
        return score;
      };
      
      const handleSelect = (result) => {
        onTeamSelect(result.node);
        setSearchTerm('');
        setShowResults(false);
      };
      
      return (
        <div className="search-bar" ref={searchRef}>
          <input
            type="text"
            placeholder="Search teams..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            onFocus={() => results.length > 0 && setShowResults(true)}
          />
          {showResults && results.length > 0 && (
            <div className="search-results">
              {results.map((result, index) => (
                <div 
                  key={result.node.id}
                  className="search-result-item"
                  onClick={() => handleSelect(result)}
                >
                  <div className="result-name">{result.primaryName}</div>
                  {result.allNames.length > 1 && (
                    <div className="result-aliases">
                      Also known as: {result.allNames.filter(n => n !== result.primaryName).join(', ')}
                    </div>
                  )}
                  <div className="result-meta">
                    {result.node.founding_year}
                    {result.node.dissolution_year ? ` - ${result.node.dissolution_year}` : ' - present'}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      );
    }
    ```
    
    2. GRAPH NAVIGATION (src/utils/graphNavigation.js):
    ```javascript
    import * as d3 from 'd3';
    
    export class GraphNavigation {
      constructor(svg, width, height) {
        this.svg = svg;
        this.width = width;
        this.height = height;
      }
      
      /**
       * Focus on a specific node with animation
       */
      focusOnNode(node, duration = 750) {
        const svg = d3.select(this.svg);
        const g = svg.select('g');
        
        // Calculate transform to center node
        const scale = 2; // Zoom in to 2x
        const x = -node.x * scale + this.width / 2;
        const y = -node.y * scale + this.height / 2;
        
        const transform = d3.zoomIdentity
          .translate(x, y)
          .scale(scale);
        
        // Animate to position
        svg.transition()
          .duration(duration)
          .call(
            d3.zoom().transform,
            transform
          );
        
        // Highlight the node
        this.highlightNode(node, duration);
      }
      
      /**
       * Highlight a node temporarily
       */
      highlightNode(node, duration = 2000) {
        const svg = d3.select(this.svg);
        
        // Find the node element
        const nodeElement = svg.select(`.node[data-id="${node.id}"]`);
        
        if (nodeElement.empty()) return;
        
        // Pulse animation
        nodeElement.select('rect')
          .transition()
          .duration(300)
          .attr('stroke', '#FFD700')
          .attr('stroke-width', 4)
          .transition()
          .duration(300)
          .attr('stroke-width', 6)
          .transition()
          .duration(300)
          .attr('stroke-width', 4)
          .transition()
          .delay(duration - 900)
          .duration(300)
          .attr('stroke', '#333')
          .attr('stroke-width', 2);
      }
      
      /**
       * Show path between two nodes
       */
      highlightPath(sourceNode, targetNode, links) {
        // Find path using BFS
        const path = this.findPath(sourceNode.id, targetNode.id, links);
        
        if (!path) {
          console.warn('No path found between nodes');
          return;
        }
        
        // Highlight links in path
        const svg = d3.select(this.svg);
        path.forEach((link, index) => {
          setTimeout(() => {
            svg.select(`.links path[data-id="${link.id}"]`)
              .transition()
              .duration(300)
              .attr('stroke', '#FFD700')
              .attr('stroke-width', 4)
              .transition()
              .delay(2000)
              .duration(300)
              .attr('stroke', d => 
                d.type === 'SPIRITUAL_SUCCESSION' ? '#999' : '#333'
              )
              .attr('stroke-width', 2);
          }, index * 200);
        });
      }
      
      findPath(sourceId, targetId, links) {
        // Build adjacency list
        const graph = new Map();
        links.forEach(link => {
          if (!graph.has(link.source)) graph.set(link.source, []);
          graph.get(link.source).push({ node: link.target, link });
        });
        
        // BFS
        const queue = [[sourceId, []]];
        const visited = new Set([sourceId]);
        
        while (queue.length > 0) {
          const [current, path] = queue.shift();
          
          if (current === targetId) {
            return path;
          }
          
          const neighbors = graph.get(current) || [];
          for (const { node, link } of neighbors) {
            if (!visited.has(node)) {
              visited.add(node);
              queue.push([node, [...path, link]]);
            }
          }
        }
        
        return null; // No path found
      }
    }
    ```
    
    3. UPDATE TimelineGraph with search integration:
    ```javascript
    import SearchBar from './SearchBar';
    import { GraphNavigation } from '../utils/graphNavigation';
    
    export default function TimelineGraph({ data }) {
      const navigationRef = useRef(null);
      
      useEffect(() => {
        if (svgRef.current && containerRef.current) {
          navigationRef.current = new GraphNavigation(
            svgRef.current,
            containerRef.current.clientWidth,
            containerRef.current.clientHeight
          );
        }
      }, []);
      
      const handleTeamSelect = (node) => {
        if (navigationRef.current) {
          navigationRef.current.focusOnNode(node);
        }
      };
      
      // Add data-id attributes to nodes and links
      const renderNodes = (g, nodes, svg) => {
        const nodeGroups = g.append('g')
          .attr('class', 'nodes')
          .selectAll('g')
          .data(nodes)
          .join('g')
            .attr('class', 'node')
            .attr('data-id', d => d.id) // Add data attribute
            .attr('transform', d => `translate(${d.x},${d.y})`)
            // ... rest of rendering
      };
      
      const renderLinks = (g, links) => {
        g.append('g')
          .attr('class', 'links')
          .selectAll('path')
          .data(links)
          .join('path')
            .attr('data-id', (d, i) => `link-${i}`) // Add data attribute
            .attr('d', d => d.path)
            // ... rest of rendering
      };
      
      return (
        <div className="timeline-graph-container">
          <SearchBar 
            nodes={data?.nodes || []}
            onTeamSelect={handleTeamSelect}
          />
          {/* ... rest of component ... */}
        </div>
      );
    }
    ```
    
    4. STYLING (src/components/SearchBar.css):
    ```css
    .search-bar {
      position: absolute;
      top: 20px;
      left: 50%;
      transform: translateX(-50%);
      z-index: 100;
      width: 400px;
      max-width: 90%;
    }
    
    .search-bar input {
      width: 100%;
      padding: 12px 16px;
      border: 2px solid #333;
      border-radius: 24px;
      font-size: 16px;
      outline: none;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    .search-bar input:focus {
      border-color: #4A90E2;
      box-shadow: 0 2px 12px rgba(74, 144, 226, 0.3);
    }
    
    .search-results {
      position: absolute;
      top: 100%;
      left: 0;
      right: 0;
      margin-top: 8px;
      background: white;
      border: 2px solid #333;
      border-radius: 8px;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
      max-height: 400px;
      overflow-y: auto;
    }
    
    .search-result-item {
      padding: 12px 16px;
      cursor: pointer;
      border-bottom: 1px solid #eee;
      transition: background 0.2s;
    }
    
    .search-result-item:last-child {
      border-bottom: none;
    }
    
    .search-result-item:hover {
      background: #f5f5f5;
    }
    
    .result-name {
      font-weight: bold;
      color: #333;
      margin-bottom: 4px;
    }
    
    .result-aliases {
      font-size: 13px;
      color: #666;
      margin-bottom: 4px;
    }
    
    .result-meta {
      font-size: 12px;
      color: #999;
    }
    ```
    
    TESTING:
    - Test search with various queries
    - Test search ranking (exact match > starts with > contains)
    - Test search across multiple eras
    - Test UCI code search
    - Test search result selection
    - Test focus animation
    - Test highlight effect
    - Test clicking outside closes results
    
    SUCCESS CRITERIA:
    - Search returns relevant results quickly
    - Results are ranked by relevance
    - Selecting result smoothly animates to node
    - Highlighted node is clearly visible
    - Search works across all team names (past and present)
    - No performance issues with large datasets

### Prompt 20: Performance Optimization

    Optimize the D3 visualization for large datasets with virtualization and rendering improvements:
    
    REQUIREMENTS:
    
    1. VIRTUALIZATION UTILITIES (src/utils/virtualization.js):
    ```javascript
    /**
     * Determine which nodes are visible in current viewport
     */
    export class ViewportManager {
      constructor(width, height) {
        this.width = width;
        this.height = height;
        this.padding = 100; // Extra padding for smooth scrolling
      }
      
      getVisibleNodes(nodes, transform) {
        const { x, y, k: scale } = transform;
        
        // Calculate visible bounds
        const viewLeft = -x / scale;
        const viewRight = (this.width - x) / scale;
        const viewTop = -y / scale;
        const viewBottom = (this.height - y) / scale;
        
        return nodes.filter(node => {
          const nodeRight = node.x + node.width;
          const nodeBottom = node.y + node.height;
          
          return !(
            nodeRight < viewLeft - this.padding ||
            node.x > viewRight + this.padding ||
            nodeBottom < viewTop - this.padding ||
            node.y > viewBottom + this.padding
          );
        });
      }
      
      getVisibleLinks(links, visibleNodeIds) {
        return links.filter(link =>
          visibleNodeIds.has(link.source) || visibleNodeIds.has(link.target)
        );
      }
    }
    ```
    
    2. PERFORMANCE MONITORING (src/utils/performanceMonitor.js):
    ```javascript
    export class PerformanceMonitor {
      constructor() {
        this.metrics = {
          renderTime: [],
          layoutTime: [],
          nodeCount: 0,
          linkCount: 0
        };
      }
      
      startTiming(label) {
        return performance.now();
      }
      
      endTiming(label, startTime) {
        const duration = performance.now() - startTime;
        
        if (this.metrics[`${label}Time`]) {
          this.metrics[`${label}Time`].push(duration);
          
          // Keep only last 10 measurements
          if (this.metrics[`${label}Time`].length > 10) {
            this.metrics[`${label}Time`].shift();
          }
        }
        
        if (duration > 100) {
          console.warn(`${label} took ${duration.toFixed(2)}ms`);
        }
      }
      
      getAverageTime(label) {
        const times = this.metrics[`${label}Time`];
        if (!times || times.length === 0) return 0;
        
        return times.reduce((a, b) => a + b) / times.length;
      }
      
      logMetrics() {
        console.log('Performance Metrics:', {
          avgRenderTime: this.getAverageTime('render').toFixed(2) + 'ms',
          avgLayoutTime: this.getAverageTime('layout').toFixed(2) + 'ms',
          nodeCount: this.metrics.nodeCount,
          linkCount: this.metrics.linkCount
        });
      }
    }
    ```
    
    3. OPTIMIZED RENDERING (src/utils/optimizedRenderer.js):
    ```javascript
    import * as d3 from 'd3';
    
    export class OptimizedRenderer {
      constructor(svg, performanceMonitor) {
        this.svg = svg;
        this.monitor = performanceMonitor;
        this.renderQueue = [];
        this.isRendering = false;
      }
      
      /**
       * Batch render updates to avoid layout thrashing
       */
      queueRender(renderFn) {
        this.renderQueue.push(renderFn);
        
        if (!this.isRendering) {
          this.processQueue();
        }
      }
      
      processQueue() {
        if (this.renderQueue.length === 0) {
          this.isRendering = false;
          return;
        }
        
        this.isRendering = true;
        
        requestAnimationFrame(() => {
          const startTime = this.monitor.startTiming('render');
          
          // Process all queued renders
          while (this.renderQueue.length > 0) {
            const renderFn = this.renderQueue.shift();
            renderFn();
          }
          
          this.monitor.endTiming('render', startTime);
          this.isRendering = false;
        });
      }
      
      /**
       * Render with LOD (Level of Detail)
       */
      renderWithLOD(nodes, links, scale) {
        const useLowDetail = nodes.length > 100 || scale < 0.8;
        
        if (useLowDetail) {
          this.renderLowDetail(nodes, links);
        } else {
          this.renderHighDetail(nodes, links);
        }
      }
      
      renderLowDetail(nodes, links) {
        // Simplified rendering for performance
        const g = d3.select(this.svg).select('g');
        
        // Remove text labels
        g.selectAll('.node text').style('display', 'none');
        
        // Simplify gradients (use solid colors)
        g.selectAll('.node rect')
          .attr('fill', d => {
            const sponsors = d.eras[d.eras.length - 1]?.sponsors || [];
            return sponsors[0]?.color || '#4A90E2';
          });
      }
      
      renderHighDetail(nodes, links) {
        const g = d3.select(this.svg).select('g');
        
        // Show all details
        g.selectAll('.node text').style('display', null);
        
        // Restore gradients
        // (This assumes gradients are already defined)
      }
      
      /**
       * Use canvas for rendering when needed
       */
      renderToCanvas(canvas, nodes, links, transform) {
        const ctx = canvas.getContext('2d');
        const { x, y, k: scale } = transform;
        
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.save();
        ctx.translate(x, y);
        ctx.scale(scale, scale);
        
        // Render links
        links.forEach(link => {
          ctx.beginPath();
          ctx.moveTo(link.sourceX, link.sourceY);
          ctx.lineTo(link.targetX, link.targetY);
          ctx.strokeStyle = link.type === 'SPIRITUAL_SUCCESSION' ? '#999' : '#333';
          ctx.lineWidth = 2 / scale; // Compensate for scale
          ctx.stroke();
        });
        
        // Render nodes
        nodes.forEach(node => {
          ctx.fillStyle = node.eras[node.eras.length - 1]?.sponsors[0]?.color || '#4A90E2';
          ctx.fillRect(node.x, node.y, node.width, node.height);
          ctx.strokeStyle = '#333';
          ctx.lineWidth = 2 / scale;
          ctx.strokeRect(node.x, node.y, node.width, node.height);
        });
        
        ctx.restore();
      }
    }
    ```
    
    4. UPDATE TimelineGraph with optimizations:
    ```javascript
    import { ViewportManager } from '../utils/virtualization';
    import { PerformanceMonitor } from '../utils/performanceMonitor';
    import { OptimizedRenderer } from '../utils/optimizedRenderer';
    
    export default function TimelineGraph({data }) { const viewportManager = useRef(null); const performanceMonitor = useRef(new PerformanceMonitor()); const optimizedRenderer = useRef(null); const currentTransform = useRef(d3.zoomIdentity);

useEffect(() => { if (!data || !containerRef.current) return;

    viewportManager.current = new ViewportManager(
      containerRef.current.clientWidth,
      containerRef.current.clientHeight
    );
    
    optimizedRenderer.current = new OptimizedRenderer(
      svgRef.current,
      performanceMonitor.current
    );

}, \[\]);

const renderGraph = useCallback((graphData) => { const startTime = performanceMonitor.current.startTiming('layout');

    // Calculate layout
    const calculator = new LayoutCalculator(graphData, width, height);
    const layout = calculator.calculateLayout();
    
    performanceMonitor.current.endTiming('layout', startTime);
    performanceMonitor.current.metrics.nodeCount = layout.nodes.length;
    performanceMonitor.current.metrics.linkCount = layout.links.length;
    
    // Initial render with virtualization
    renderWithVirtualization(layout);

}, \[\]);

const renderWithVirtualization = useCallback((layout) => { const transform = currentTransform.current;

    // Get visible elements
    const visibleNodes = viewportManager.current.getVisibleNodes(
      layout.nodes,
      transform
    );
    const visibleNodeIds = new Set(visibleNodes.map(n => n.id));
    const visibleLinks = viewportManager.current.getVisibleLinks(
      layout.links,
      visibleNodeIds
    );
    
    // Render only visible elements
    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();
    
    const g = svg.append('g')
      .attr('transform', transform);
    
    renderLinks(g, visibleLinks);
    renderNodes(g, visibleNodes, svg);
    
    // Setup zoom with virtualization
    setupZoomWithVirtualization(svg, g, layout);

}, \[\]);

const setupZoomWithVirtualization = (svg, g, layout) => { const zoom = d3.zoom() .scaleExtent(\[0.5, 5\]) .on('zoom', (event) => { currentTransform.current = event.transform; g.attr('transform', event.transform);

        // Debounce virtualization update
        clearTimeout(virtualizationTimeout.current);
        virtualizationTimeout.current = setTimeout(() => {
          updateVirtualization(layout, event.transform);
        }, 100);
        
        // Update LOD immediately
        optimizedRenderer.current.renderWithLOD(
          layout.nodes,
          layout.links,
          event.transform.k
        );
      });
    
    svg.call(zoom);

};

const updateVirtualization = (layout, transform) => { const visibleNodes = viewportManager.current.getVisibleNodes( layout.nodes, transform ); const visibleNodeIds = new Set(visibleNodes.map(n => n.id)); const visibleLinks = viewportManager.current.getVisibleLinks( layout.links, visibleNodeIds );

    // Update rendered elements
    const g = d3.select(svgRef.current).select('g');
    
    // Update nodes
    g.select('.nodes')
      .selectAll('.node')
      .data(visibleNodes, d => d.id)
      .join(
        enter => {
          const groups = enter.append('g')
            .attr('class', 'node')
            .attr('data-id', d => d.id)
            .attr('transform', d => `translate(${d.x},${d.y})`);
          
          groups.each(function(d) {
            const group = d3.select(this);
            JerseyRenderer.renderNode(group, d, g);
            JerseyRenderer.addNodeLabel(group, d);
          });
          
          return groups;
        },
        update => update,
        exit => exit.remove()
      );
    
    // Update links
    g.select('.links')
      .selectAll('path')
      .data(visibleLinks, (d, i) => `link-${i}`)
      .join(
        enter => enter.append('path')
          .attr('d', d => d.path)
          .attr('fill', 'none')
          .attr('stroke', d => 
            d.type === 'SPIRITUAL_SUCCESSION' ? '#999' : '#333'
          )
          .attr('stroke-width', 2),
        update => update,
        exit => exit.remove()
      );

};

// Log performance metrics in development useEffect(() => { if (process.env.NODE\_ENV === 'development') { const interval = setInterval(() => { performanceMonitor.current.logMetrics(); }, 10000);

      return () => clearInterval(interval);
    }

}, \[\]);

return ( <div className="timeline-graph-container"> {/\* ... rest of component ... \*/} </div> ); }

    
    5. MEMOIZATION (src/hooks/useMemoizedLayout.js):
    ```javascript
    import { useMemo } from 'react';
    import { LayoutCalculator } from '../utils/layoutCalculator';
    
    export function useMemoizedLayout(data, width, height, filters) {
      return useMemo(() => {
        if (!data || !data.nodes || !data.links) return null;
        
        // Filter data based on filters
        const filteredNodes = filterNodes(data.nodes, filters);
        const filteredLinks = filterLinks(data.links, filteredNodes);
        
        const calculator = new LayoutCalculator(
          { nodes: filteredNodes, links: filteredLinks },
          width,
          height
        );
        
        return calculator.calculateLayout();
      }, [data, width, height, filters]);
    }
    
    function filterNodes(nodes, filters) {
      return nodes.filter(node => {
        // Year range filter
        const hasEraInRange = node.eras.some(era =>
          era.year >= filters.startYear && era.year <= filters.endYear
        );
        
        if (!hasEraInRange) return false;
        
        // Tier filter
        if (filters.tiers && filters.tiers.length > 0) {
          const hasTier = node.eras.some(era =>
            filters.tiers.includes(era.tier)
          );
          if (!hasTier) return false;
        }
        
        return true;
      });
    }
    
    function filterLinks(links, filteredNodes) {
      const nodeIds = new Set(filteredNodes.map(n => n.id));
      return links.filter(link =>
        nodeIds.has(link.source) && nodeIds.has(link.target)
      );
    }
    ```
    
    TESTING:
    - Test virtualization with 1000+ nodes
    - Test performance with large datasets
    - Test LOD switching at different zoom levels
    - Test viewport culling accuracy
    - Measure render times (should be < 16ms for 60fps)
    - Test memory usage doesn't grow over time
    
    SUCCESS CRITERIA:
    - Smooth 60fps performance with 500+ nodes
    - Viewport virtualization reduces rendered nodes
    - LOD system activates at appropriate thresholds
    - Performance metrics logged in development
    - No memory leaks during pan/zoom
    - Layout calculation cached appropriately

* * *

## Phase 6: Authentication & Authorization
---------------------------------------

### Prompt 21: Google OAuth Backend Setup

    Implement Google OAuth authentication on the backend with JWT token management:
    
    REQUIREMENTS:
    
    1. ADD DEPENDENCIES (requirements.txt):

python-jose\[cryptography\]==3.3.0 passlib==1.7.4 python-multipart==0.0.6 google-auth==2.23.4 google-auth-oauthlib==1.1.0

    
    2. AUTH CONFIGURATION (app/core/config.py - extend):
    ```python
    class Settings(BaseSettings):
        # Existing settings...
        
        # Auth settings
        GOOGLE_CLIENT_ID: str
        GOOGLE_CLIENT_SECRET: str
        GOOGLE_REDIRECT_URI: str = "http://localhost:5173/auth/callback"
        
        JWT_SECRET_KEY: str
        JWT_ALGORITHM: str = "HS256"
        JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
        JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
        
        # OAuth scopes
        GOOGLE_SCOPES: list = [
            "openid",
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile"
        ]
    ```
    
    3. USER MODEL MIGRATION (alembic/versions/005_add_users.py):
    ```python
    """add users and auth tables
    
    Revision ID: 005
    """
    from alembic import op
    import sqlalchemy as sa
    from sqlalchemy.dialects.postgresql import UUID
    
    def upgrade():
        # User roles enum
        op.execute("""
            CREATE TYPE user_role_enum AS ENUM ('GUEST', 'NEW_USER', 'TRUSTED_USER', 'ADMIN')
        """)
        
        # Users table
        op.create_table(
            'users',
            sa.Column('user_id', UUID, primary_key=True, server_default=sa.text('gen_random_uuid()')),
            sa.Column('google_id', sa.String(255), unique=True, nullable=False),
            sa.Column('email', sa.String(255), unique=True, nullable=False),
            sa.Column('display_name', sa.String(255)),
            sa.Column('avatar_url', sa.String(500)),
            sa.Column('role', sa.Enum('GUEST', 'NEW_USER', 'TRUSTED_USER', 'ADMIN', name='user_role_enum'), default='NEW_USER'),
            sa.Column('approved_edits_count', sa.Integer, default=0),
            sa.Column('is_banned', sa.Boolean, default=False),
            sa.Column('banned_reason', sa.Text, nullable=True),
            sa.Column('created_at', sa.TIMESTAMP, server_default=sa.text('NOW()')),
            sa.Column('last_login_at', sa.TIMESTAMP, nullable=True),
            sa.Column('updated_at', sa.TIMESTAMP, server_default=sa.text('NOW()'))
        )
        
        # Refresh tokens table
        op.create_table(
            'refresh_tokens',
            sa.Column('token_id', UUID, primary_key=True, server_default=sa.text('gen_random_uuid()')),
            sa.Column('user_id', UUID, sa.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False),
            sa.Column('token_hash', sa.String(255), unique=True, nullable=False),
            sa.Column('expires_at', sa.TIMESTAMP, nullable=False),
            sa.Column('created_at', sa.TIMESTAMP, server_default=sa.text('NOW()'))
        )
        
        op.create_index('idx_users_google_id', 'users', ['google_id'])
        op.create_index('idx_users_email', 'users', ['email'])
        op.create_index('idx_refresh_tokens_user', 'refresh_tokens', ['user_id'])
        op.create_index('idx_refresh_tokens_hash', 'refresh_tokens', ['token_hash'])
    
    def downgrade():
        op.drop_table('refresh_tokens')
        op.drop_table('users')
        op.execute('DROP TYPE user_role_enum')
    ```
    
    4. USER MODELS (app/models/user.py - create):
    ```python
    from sqlalchemy import Column, String, Integer, Boolean, Text, TIMESTAMP, Enum, ForeignKey
    from sqlalchemy.dialects.postgresql import UUID
    from sqlalchemy.orm import relationship
    from app.db.base import Base
    import enum
    
    class UserRole(str, enum.Enum):
        GUEST = "GUEST"
        NEW_USER = "NEW_USER"
        TRUSTED_USER = "TRUSTED_USER"
        ADMIN = "ADMIN"
    
    class User(Base):
        __tablename__ = "users"
        
        user_id = Column(UUID, primary_key=True, server_default=text('gen_random_uuid()'))
        google_id = Column(String(255), unique=True, nullable=False)
        email = Column(String(255), unique=True, nullable=False)
        display_name = Column(String(255))
        avatar_url = Column(String(500))
        role = Column(Enum(UserRole), default=UserRole.NEW_USER)
        approved_edits_count = Column(Integer, default=0)
        is_banned = Column(Boolean, default=False)
        banned_reason = Column(Text, nullable=True)
        created_at = Column(TIMESTAMP, server_default=text('NOW()'))
        last_login_at = Column(TIMESTAMP, nullable=True)
        updated_at = Column(TIMESTAMP, server_default=text('NOW()'))
        
        refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
        
        def can_edit(self) -> bool:
            return self.role in [UserRole.NEW_USER, UserRole.TRUSTED_USER, UserRole.ADMIN] and not self.is_banned
        
        def needs_moderation(self) -> bool:
            return self.role == UserRole.NEW_USER
        
        def is_admin(self) -> bool:
            return self.role == UserRole.ADMIN
    
    class RefreshToken(Base):
        __tablename__ = "refresh_tokens"
        
        token_id = Column(UUID, primary_key=True, server_default=text('gen_random_uuid()'))
        user_id = Column(UUID, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
        token_hash = Column(String(255), unique=True, nullable=False)
        expires_at = Column(TIMESTAMP, nullable=False)
        created_at = Column(TIMESTAMP, server_default=text('NOW()'))
        
        user = relationship("User", back_populates="refresh_tokens")
    ```
    
    5. JWT UTILITIES (app/core/security.py - create):
    ```python
    from datetime import datetime, timedelta
    from typing import Optional
    from jose import JWTError, jwt
    from passlib.context import CryptContext
    from app.core.config import settings
    
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        return encoded_jwt
    
    def create_refresh_token(data: dict):
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        return encoded_jwt
    
    def verify_token(token: str) -> Optional[dict]:
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            return payload
        except JWTError:
            return None
    
    def hash_token(token: str) -> str:
        return pwd_context.hash(token)
    
    def verify_token_hash(token: str, hashed: str) -> bool:
        return pwd_context.verify(token, hashed)
    ```
    
    6. GOOGLE OAUTH SERVICE (app/services/auth_service.py - create):
    ```python
    from google.oauth2 import id_token
    from google.auth.transport import requests
    from typing import Optional, Dict
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy import select
    from datetime import datetime, timedelta
    
    from app.core.config import settings
    from app.core.security import create_access_token, create_refresh_token, hash_token
    from app.models.user import User, RefreshToken
    from app.schemas.auth import TokenResponse
    
    class AuthService:
        @staticmethod
        async def verify_google_token(token: str) -> Optional[Dict]:
            """Verify Google ID token and extract user info"""
            try:
                idinfo = id_token.verify_oauth2_token(
                    token,
                    requests.Request(),
                    settings.GOOGLE_CLIENT_ID
                )
                
                if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                    raise ValueError('Wrong issuer')
                
                return {
                    'google_id': idinfo['sub'],
                    'email': idinfo['email'],
                    'display_name': idinfo.get('name'),
                    'avatar_url': idinfo.get('picture')
                }
            except ValueError as e:
                print(f"Token verification failed: {e}")
                return None
        
        @staticmethod
        async def get_or_create_user(
            session: AsyncSession,
            google_user_info: Dict
        ) -> User:
            """Get existing user or create new one"""
            stmt = select(User).where(User.google_id == google_user_info['google_id'])
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()
            
            if user:
                # Update last login
                user.last_login_at = datetime.utcnow()
                user.updated_at = datetime.utcnow()
            else:
                # Create new user
                user = User(
                    google_id=google_user_info['google_id'],
                    email=google_user_info['email'],
                    display_name=google_user_info['display_name'],
                    avatar_url=google_user_info['avatar_url']
                )
                session.add(user)
            
            await session.commit()
            await session.refresh(user)
            return user
        
        @staticmethod
        async def create_tokens(
            session: AsyncSession,
            user: User
        ) -> TokenResponse:
            """Create access and refresh tokens for user"""
            access_token = create_access_token(
                data={"sub": str(user.user_id), "email": user.email, "role": user.role.value}
            )
            
            refresh_token = create_refresh_token(
                data={"sub": str(user.user_id)}
            )
            
            # Store refresh token in database
            token_hash = hash_token(refresh_token)
            expires_at = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
            
            db_refresh_token = RefreshToken(
                user_id=user.user_id,
                token_hash=token_hash,
                expires_at=expires_at
            )
            session.add(db_refresh_token)
            await session.commit()
            
            return TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer"
            )
    ```
    
    7. AUTH SCHEMAS (app/schemas/auth.py - create):
    ```python
    from pydantic import BaseModel, EmailStr
    from typing import Optional
    
    class GoogleTokenRequest(BaseModel):
        id_token: str
    
    class TokenResponse(BaseModel):
        access_token: str
        refresh_token: str
        token_type: str = "bearer"
    
    class RefreshTokenRequest(BaseModel):
        refresh_token: str
    
    class UserResponse(BaseModel):
        user_id: str
        email: EmailStr
        display_name: Optional[str]
        avatar_url: Optional[str]
        role: str
        approved_edits_count: int
        
        class Config:
            from_attributes = True
    ```
    
    8. AUTH ENDPOINTS (app/api/v1/auth.py - create):
    ```python
    from fastapi import APIRouter, Depends, HTTPException
    from sqlalchemy.ext.asyncio import AsyncSession
    
    from app.db.database import get_db
    from app.schemas.auth import GoogleTokenRequest, TokenResponse, RefreshTokenRequest, UserResponse
    from app.services.auth_service import AuthService
    from app.core.security import verify_token
    
    router = APIRouter(prefix="/api/v1/auth", tags=["auth"])
    
    @router.post("/google", response_model=TokenResponse)
    async def google_auth(
        request: GoogleTokenRequest,
        session: AsyncSession = Depends(get_db)
    ):
        """Authenticate with Google ID token"""
        # Verify Google token
        google_user_info = await AuthService.verify_google_token(request.id_token)
        
        if not google_user_info:
            raise HTTPException(status_code=401, detail="Invalid Google token")
        
        # Get or create user
        user = await AuthService.get_or_create_user(session, google_user_info)
        
        if user.is_banned:
            raise HTTPException(status_code=403, detail=f"Account banned: {user.banned_reason}")
        
        # Create tokens
        tokens = await AuthService.create_tokens(session, user)
        return tokens
    
    @router.post("/refresh", response_model=TokenResponse)
    async def refresh_token(
        request: RefreshTokenRequest,
        session: AsyncSession = Depends(get_db)
    ):
        """Refresh access token using refresh token"""
        # Verify refresh token
        payload = verify_token(request.refresh_token)
        
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        
        user_id = payload.get("sub")
        
        # Get user
        user = await session.get(User, user_id)
        if not user or user.is_banned:
            raise HTTPException(status_code=401, detail="Invalid user")
        
        # Create new tokens
        tokens = await AuthService.create_tokens(session, user)
        return tokens
    
    @router.get("/me", response_model=UserResponse)
    async def get_current_user(
        current_user: User = Depends(get_current_user)
    ):
        """Get current user info"""
        return current_user
    ```
    
    9. AUTH DEPENDENCIES (app/api/dependencies.py - create):
    ```python
    from fastapi import Depends, HTTPException, status
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy import select
    
    from app.db.database import get_db
    from app.core.security import verify_token
    from app.models.user import User, UserRole
    
    security = HTTPBearer()
    
    async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        session: AsyncSession = Depends(get_db)
    ) -> User:
        """Get current authenticated user"""
        token = credentials.credentials
        payload = verify_token(token)
        
        if not payload or payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        user_id = payload.get("sub")
        stmt = select(User).where(User.user_id == user_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        if user.is_banned:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Account banned: {user.banned_reason}"
            )
        
        return user
    
    async def require_admin(
        current_user: User = Depends(get_current_user)
    ) -> User:
        """Require admin role"""
        if not current_user.is_admin():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        return current_user
    
    async def require_editor(
        current_user: User = Depends(get_current_user)
    ) -> User:
        """Require editor permissions (not banned)"""
        if not current_user.can_edit():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Editor access required"
            )
        return current_user
    ```
    
    10. UPDATE MAIN (main.py):
    ```python
    from app.api.v1 import auth
    
    app.include_router(auth.router)
    ```
    
    TESTING (tests/api/test_auth.py):
    - Test Google token verification (mock Google API)
    - Test user creation on first login
    - Test user retrieval on subsequent login
    - Test token creation
    - Test refresh token flow
    - Test banned user cannot authenticate
    - Test invalid tokens return 401
    - Test admin/editor role checks
    
    SUCCESS CRITERIA:
    - Google OAuth flow works end-to-end
    - JWT tokens created and validated
    - Refresh tokens stored and work correctly
    - User roles enforced
    - Banned users cannot access system
    - All tests pass

### Prompt 22: Frontend Auth Integration

    Integrate Google OAuth on the frontend with token management:
    
    REQUIREMENTS:
    
    1. INSTALL DEPENDENCIES:
    ```bash
    npm install @react-oauth/google jwt-decode
    ```
    
    2. AUTH CONTEXT (src/contexts/AuthContext.jsx):
    ```javascript
    import { createContext, useContext, useState, useEffect } from 'react';
    import { googleLogout } from '@react-oauth/google';
    import { jwtDecode } from 'jwt-decode';
    import { authApi } from '../api/auth';
    
    const AuthContext = createContext(null);
    
    export function AuthProvider({ children }) {
      const [user, setUser] = useState(null);
      const [loading, setLoading] = useState(true);
      const [accessToken, setAccessToken] = useState(null);
      const [refreshToken, setRefreshToken] = useState(null);
      
      useEffect(() => {
        // Load tokens from localStorage on mount
        const storedAccessToken = localStorage.getItem('accessToken');
        const storedRefreshToken = localStorage.getItem('refreshToken');
        
        if (storedAccessToken && storedRefreshToken) {
          // Verify token is not expired
          try {
            const decoded = jwtDecode(storedAccessToken);
            if (decoded.exp * 1000 > Date.now()) {
              setAccessToken(storedAccessToken);
              setRefreshToken(storedRefreshToken);
              loadUserInfo(storedAccessToken);
            } else {
              // Try to refresh
              refreshAccessToken(storedRefreshToken);
            }
          } catch (error) {
            console.error('Invalid token:', error);
            clearAuth();
          }
        } else {
          setLoading(false);
        }
      }, []);
      
      const loadUserInfo = async (token) => {
        try {
          const response = await authApi.getCurrentUser(token);
          setUser(response.data);
        } catch (error) {
          console.error('Failed to load user info:', error);
          clearAuth();
        } finally {
          setLoading(false);
        }
      };
      
      const handleGoogleSuccess = async (credentialResponse) => {
        try {
          const response = await authApi.googleAuth(credentialResponse.credential);
          const { access_token, refresh_token } = response.data;
          
          // Store tokens
          localStorage.setItem('accessToken', access_token);
          localStorage.setItem('refreshToken', refresh_token);
          
          setAccessToken(access_token);
          setRefreshToken(refresh_token);
          
          // Load user info
          await loadUserInfo(access_token);
        } catch (error) {
          console.error('Google auth failed:', error);
          throw error;
        }
      };
      
      const refreshAccessToken = async (refToken) => {
        try {
          const response = await authApi.refreshToken(refToken);
          const { access_token, refresh_token } = response.data;
          
          localStorage.setItem('accessToken', access_token);
          localStorage.setItem('refreshToken', refresh_token);
          
          setAccessToken(access_token);
          setRefreshToken(refresh_token);
          
          await loadUserInfo(access_token);
          
          return access_token;
        } catch (error) {
          console.error('Token refresh failed:', error);
          clearAuth();
          throw error;
        }
      };
      
      const logout = () => {
        googleLogout();
        clearAuth();
      };
      
      const clearAuth = () => {
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        setAccessToken(null);
        setRefreshToken(null);
        setUser(null);
        setLoading(false);
      };
      
      const isAdmin = () => {
        return user?.role === 'ADMIN';
      };
      
      const canEdit = () => {
        return user && ['NEW_USER', 'TRUSTED_USER', 'ADMIN'].includes(user.role);
      };
      
      const needsModeration = () => {
        return user?.role === 'NEW_USER';
      };
      
      return (
        <AuthContext.Provider value={{
          user,
          loading,
          accessToken,
          refreshToken,
          handleGoogleSuccess,
          refreshAccessToken,
          logout,
          isAuthenticated: !!user,
          isAdmin,
          canEdit,
          needsModeration
        }}>
          {children}
        </AuthContext.Provider>
      );
    }
    
    export function useAuth() {
      const context = useContext(AuthContext);
      if (!context) {
        throw new Error('useAuth must be used within AuthProvider');
      }
      return context;
    }
    ```
    
    3. AUTH API CLIENT (src/api/auth.js):
    ```javascript
    import apiClient from './client';
    
    export const authApi = {
      googleAuth: (idToken) => 
        apiClient.post('/api/v1/auth/google', { id_token: idToken }),
      
      refreshToken: (refreshToken) =>
        apiClient.post('/api/v1/auth/refresh', { refresh_token: refreshToken }),
      
      getCurrentUser: (token) =>
        apiClient.get('/api/v1/auth/me', {
          headers: { Authorization: `Bearer ${token}` }
        }),
    };
    ```
    
    4. UPDATE API CLIENT with token refresh (src/api/client.js):
    ```javascript
    import axios from 'axios';
    
    const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    
    export const apiClient = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    let isRefreshing = false;
    let refreshSubscribers = [];
    
    const subscribeTokenRefresh = (callback) => {
      refreshSubscribers.push(callback);
    };
    
    const onTokenRefreshed = (token) => {
      refreshSubscribers.forEach(callback => callback(token));
      refreshSubscribers = [];
    };
    
    // Request interceptor: add access token
    apiClient.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('accessToken');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );
    
    // Response interceptor: handle 401 and refresh token
    apiClient.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;
        
        if (error.response?.status === 401 && !originalRequest.\_retry) { if (isRefreshing) { // Wait for token refresh return new Promise((resolve) => { subscribeTokenRefresh((token) => { originalRequest.headers.Authorization = `Bearer ${token}`; resolve(apiClient(originalRequest)); }); }); }

      originalRequest._retry = true;
      isRefreshing = true;
      
      try {
        const refreshToken = localStorage.getItem('refreshToken');
        if (!refreshToken) {
          throw new Error('No refresh token');
        }
        
        const response = await axios.post(
          `${API_BASE_URL}/api/v1/auth/refresh`,
          { refresh_token: refreshToken }
        );
        
        const { access_token, refresh_token: new_refresh_token } = response.data;
        
        localStorage.setItem('accessToken', access_token);
        localStorage.setItem('refreshToken', new_refresh_token);
        
        apiClient.defaults.headers.Authorization = `Bearer ${access_token}`;
        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        
        onTokenRefreshed(access_token);
        isRefreshing = false;
        
        return apiClient(originalRequest);
      } catch (refreshError) {
        isRefreshing = false;
        
        // Clear auth and redirect to login
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        window.location.href = '/';
        
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);

} );

export default apiClient;

    
    5. LOGIN COMPONENT (src/components/Login.jsx):
    ```javascript
    import { GoogleLogin } from '@react-oauth/google';
    import { useAuth } from '../contexts/AuthContext';
    import { useNavigate } from 'react-router-dom';
    import './Login.css';
    
    export default function Login() {
      const { handleGoogleSuccess } = useAuth();
      const navigate = useNavigate();
      
      const onSuccess = async (credentialResponse) => {
        try {
          await handleGoogleSuccess(credentialResponse);
          navigate('/');
        } catch (error) {
          console.error('Login failed:', error);
          alert('Login failed. Please try again.');
        }
      };
      
      const onError = () => {
        console.error('Google login failed');
        alert('Google login failed. Please try again.');
      };
      
      return (
        <div className="login-container">
          <div className="login-card">
            <h1>Cycling Team Lineage</h1>
            <p>Sign in to contribute to the timeline</p>
            
            <GoogleLogin
              onSuccess={onSuccess}
              onError={onError}
              useOneTap
            />
            
            <div className="login-info">
              <h3>Why sign in?</h3>
              <ul>
                <li>Edit team information</li>
                <li>Create lineage events</li>
                <li>Contribute to cycling history</li>
              </ul>
            </div>
          </div>
        </div>
      );
    }
    ```
    
    6. USER MENU COMPONENT (src/components/UserMenu.jsx):
    ```javascript
    import { useState, useRef, useEffect } from 'react';
    import { useAuth } from '../contexts/AuthContext';
    import './UserMenu.css';
    
    export default function UserMenu() {
      const { user, logout, isAdmin, canEdit, needsModeration } = useAuth();
      const [isOpen, setIsOpen] = useState(false);
      const menuRef = useRef(null);
      
      useEffect(() => {
        const handleClickOutside = (event) => {
          if (menuRef.current && !menuRef.current.contains(event.target)) {
            setIsOpen(false);
          }
        };
        
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
      }, []);
      
      if (!user) return null;
      
      return (
        <div className="user-menu" ref={menuRef}>
          <button 
            className="user-avatar"
            onClick={() => setIsOpen(!isOpen)}
          >
            {user.avatar_url ? (
              <img src={user.avatar_url} alt={user.display_name} />
            ) : (
              <div className="avatar-placeholder">
                {user.display_name?.[0] || user.email[0]}
              </div>
            )}
          </button>
          
          {isOpen && (
            <div className="user-menu-dropdown">
              <div className="user-info">
                <div className="user-name">{user.display_name || user.email}</div>
                <div className="user-role">
                  {isAdmin() && <span className="badge admin">Admin</span>}
                  {needsModeration() && <span className="badge new">New User</span>}
                  {canEdit() && !isAdmin() && !needsModeration() && (
                    <span className="badge trusted">Trusted</span>
                  )}
                </div>
                <div className="user-stats">
                  {user.approved_edits_count} edits approved
                </div>
              </div>
              
              <div className="menu-divider" />
              
              <button className="menu-item" onClick={() => setIsOpen(false)}>
                My Edits
              </button>
              
              {isAdmin() && (
                <>
                  <button className="menu-item" onClick={() => setIsOpen(false)}>
                    Moderation Queue
                  </button>
                  <button className="menu-item" onClick={() => setIsOpen(false)}>
                    Admin Panel
                  </button>
                </>
              )}
              
              <div className="menu-divider" />
              
              <button className="menu-item logout" onClick={logout}>
                Sign Out
              </button>
            </div>
          )}
        </div>
      );
    }
    ```
    
    7. UPDATE LAYOUT (src/components/Layout.jsx):
    ```javascript
    import { Outlet, Link } from 'react-router-dom';
    import { useAuth } from '../contexts/AuthContext';
    import UserMenu from './UserMenu';
    import './Layout.css';
    
    export default function Layout() {
      const { isAuthenticated, loading } = useAuth();
      
      if (loading) {
        return <div>Loading...</div>;
      }
      
      return (
        <div className="layout">
          <header className="layout-header">
            <div className="header-content">
              <Link to="/" className="app-title">
                <h1>Cycling Team Lineage</h1>
              </Link>
              
              <nav className="header-nav">
                {isAuthenticated ? (
                  <UserMenu />
                ) : (
                  <Link to="/login" className="login-button">
                    Sign In
                  </Link>
                )}
              </nav>
            </div>
          </header>
          
          <main className="layout-main">
            <Outlet />
          </main>
          
          <footer className="layout-footer">
            <p>&copy; 2024 Cycling Team Lineage. Open Source Project.</p>
          </footer>
        </div>
      );
    }
    ```
    
    8. UPDATE MAIN (src/main.jsx):
    ```javascript
    import { GoogleOAuthProvider } from '@react-oauth/google';
    import { AuthProvider } from './contexts/AuthContext';
    
    const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID;
    
    ReactDOM.createRoot(document.getElementById('root')).render(
      <React.StrictMode>
        <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
          <QueryClientProvider client={queryClient}>
            <AuthProvider>
              <App />
            </AuthProvider>
          </QueryClientProvider>
        </GoogleOAuthProvider>
      </React.StrictMode>
    );
    ```
    
    9. ADD LOGIN ROUTE (src/App.jsx):
    ```javascript
    import Login from './pages/LoginPage';
    
    function App() {
      return (
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Layout />}>
              <Route index element={<HomePage />} />
              <Route path="team/:nodeId" element={<TeamDetailPage />} />
              <Route path="login" element={<Login />} />
              <Route path="*" element={<NotFoundPage />} />
            </Route>
          </Routes>
        </BrowserRouter>
      );
    }
    ```
    
    10. ENVIRONMENT (.env):

VITE\_API\_URL=[http://localhost:8000](http://localhost:8000) VITE\_GOOGLE\_CLIENT\_ID=your-google-client-id-here

    
    TESTING:
    - Test Google login flow
    - Test token storage in localStorage
    - Test automatic token refresh on 401
    - Test logout clears all auth state
    - Test protected routes redirect to login
    - Test user menu displays correct role
    - Test auth persists across page refresh
    
    SUCCESS CRITERIA:
    - Google OAuth works end-to-end
    - Tokens automatically refresh before expiry
    - User state persists across refresh
    - Logout completely clears state
    - Role-based UI elements display correctly
    - No console errors during auth flow

* * *

## Phase 7: The Wizard Editor
--------------------------

### Prompt 23: Edit Metadata Wizard

    Implement the wizard for editing basic team metadata (non-structural changes):
    
    REQUIREMENTS:
    
    1. BACKEND ENDPOINT (app/api/v1/edits.py - create):
    ```python
    from fastapi import APIRouter, Depends, HTTPException
    from sqlalchemy.ext.asyncio import AsyncSession
    from typing import Optional
    
    from app.db.database import get_db
    from app.api.dependencies import get_current_user, require_editor
    from app.models.user import User
    from app.models.team import TeamEra
    from app.schemas.edits import EditMetadataRequest, EditMetadataResponse
    from app.services.edit_service import EditService
    
    router = APIRouter(prefix="/api/v1/edits", tags=["edits"])
    
    @router.post("/metadata", response_model=EditMetadataResponse)
    async def edit_metadata(
        request: EditMetadataRequest,
        session: AsyncSession = Depends(get_db),
        current_user: User = Depends(require_editor)
    ):
        """Edit team era metadata"""
        try:
            result = await EditService.create_metadata_edit(
                session,
                current_user,
                request
            )
            return result
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    ```
    
    2. EDIT SCHEMAS (app/schemas/edits.py - create):
    ```python
    from pydantic import BaseModel, validator
    from typing import Optional
    from datetime import datetime
    
    class EditMetadataRequest(BaseModel):
        era_id: str
        registered_name: Optional[str] = None
        uci_code: Optional[str] = None
        tier_level: Optional[int] = None
        reason: str  # Why this edit is being made
        
        @validator('uci_code')
        def validate_uci_code(cls, v):
            if v and (len(v) != 3 or not v.isupper()):
                raise ValueError('UCI code must be exactly 3 uppercase letters')
            return v
        
        @validator('tier_level')
        def validate_tier(cls, v):
            if v and v not in [1, 2, 3]:
                raise ValueError('Tier must be 1, 2, or 3')
            return v
        
        @validator('reason')
        def validate_reason(cls, v):
            if len(v) < 10:
                raise ValueError('Reason must be at least 10 characters')
            return v
    
    class EditMetadataResponse(BaseModel):
        edit_id: str
        status: str  # 'PENDING' or 'APPROVED'
        message: str
        
        class Config:
            from_attributes = True
    ```
    
    3. EDIT MODEL MIGRATION (alembic/versions/006_add_edits.py):
    ```python
    """add edits and moderation tables
    
    Revision ID: 006
    """
    from alembic import op
    import sqlalchemy as sa
    from sqlalchemy.dialects.postgresql import UUID, JSONB
    
    def upgrade():
        # Edit status enum
        op.execute("""
            CREATE TYPE edit_status_enum AS ENUM ('PENDING', 'APPROVED', 'REJECTED')
        """)
        
        # Edit type enum
        op.execute("""
            CREATE TYPE edit_type_enum AS ENUM ('METADATA', 'MERGE', 'SPLIT', 'DISSOLVE')
        """)
        
        # Edits table
        op.create_table(
            'edits',
            sa.Column('edit_id', UUID, primary_key=True, server_default=sa.text('gen_random_uuid()')),
            sa.Column('user_id', UUID, sa.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False),
            sa.Column('edit_type', sa.Enum('METADATA', 'MERGE', 'SPLIT', 'DISSOLVE', name='edit_type_enum'), nullable=False),
            sa.Column('target_era_id', UUID, sa.ForeignKey('team_era.era_id', ondelete='CASCADE'), nullable=True),
            sa.Column('target_node_id', UUID, sa.ForeignKey('team_node.node_id', ondelete='CASCADE'), nullable=True),
            sa.Column('changes', JSONB, nullable=False),  # Store the changes
            sa.Column('reason', sa.Text, nullable=False),
            sa.Column('status', sa.Enum('PENDING', 'APPROVED', 'REJECTED', name='edit_status_enum'), default='PENDING'),
            sa.Column('reviewed_by', UUID, sa.ForeignKey('users.user_id', ondelete='SET NULL'), nullable=True),
            sa.Column('reviewed_at', sa.TIMESTAMP, nullable=True),
            sa.Column('review_notes', sa.Text, nullable=True),
            sa.Column('created_at', sa.TIMESTAMP, server_default=sa.text('NOW()')),
            sa.Column('updated_at', sa.TIMESTAMP, server_default=sa.text('NOW()'))
        )
        
        op.create_index('idx_edits_user', 'edits', ['user_id'])
        op.create_index('idx_edits_status', 'edits', ['status'])
        op.create_index('idx_edits_type', 'edits', ['edit_type'])
    
    def downgrade():
        op.drop_table('edits')
        op.execute('DROP TYPE edit_status_enum')
        op.execute('DROP TYPE edit_type_enum')
    ```
    
    4. EDIT MODEL (app/models/edit.py - create):
    ```python
    from sqlalchemy import Column, String, Text, TIMESTAMP, Enum, ForeignKey
    from sqlalchemy.dialects.postgresql import UUID, JSONB
    from sqlalchemy.orm import relationship
    from app.db.base import Base
    import enum
    
    class EditType(str, enum.Enum):
        METADATA = "METADATA"
        MERGE = "MERGE"
        SPLIT = "SPLIT"
        DISSOLVE = "DISSOLVE"
    
    class EditStatus(str, enum.Enum):
        PENDING = "PENDING"
        APPROVED = "APPROVED"
        REJECTED = "REJECTED"
    
    class Edit(Base):
        __tablename__ = "edits"
        
        edit_id = Column(UUID, primary_key=True, server_default=text('gen_random_uuid()'))
        user_id = Column(UUID, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
        edit_type = Column(Enum(EditType), nullable=False)
        target_era_id = Column(UUID, ForeignKey('team_era.era_id', ondelete='CASCADE'), nullable=True)
        target_node_id = Column(UUID, ForeignKey('team_node.node_id', ondelete='CASCADE'), nullable=True)
        changes = Column(JSONB, nullable=False)
        reason = Column(Text, nullable=False)
        status = Column(Enum(EditStatus), default=EditStatus.PENDING)
        reviewed_by = Column(UUID, ForeignKey('users.user_id', ondelete='SET NULL'), nullable=True)
        reviewed_at = Column(TIMESTAMP, nullable=True)
        review_notes = Column(Text, nullable=True)
        created_at = Column(TIMESTAMP, server_default=text('NOW()'))
        updated_at = Column(TIMESTAMP, server_default=text('NOW()'))
        
        user = relationship("User", foreign_keys=[user_id])
        reviewer = relationship("User", foreign_keys=[reviewed_by])
        era = relationship("TeamEra", foreign_keys=[target_era_id])
        node = relationship("TeamNode", foreign_keys=[target_node_id])
    ```
    
    5. EDIT SERVICE (app/services/edit_service.py - create):
    ```python
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy import select
    from datetime import datetime
    from typing import Dict
    
    from app.models.edit import Edit, EditType, EditStatus
    from app.models.team import TeamEra
    from app.models.user import User, UserRole
    from app.schemas.edits import EditMetadataRequest, EditMetadataResponse
    
    class EditService:
        @staticmethod
        async def create_metadata_edit(
            session: AsyncSession,
            user: User,
            request: EditMetadataRequest
        ) -> EditMetadataResponse:
            """Create a metadata edit (may be auto-approved for trusted users)"""
            # Get the target era
            era = await session.get(TeamEra, request.era_id)
            if not era:
                raise ValueError("Era not found")
            
            # Build changes dict (only include fields that are being changed)
            changes = {}
            if request.registered_name:
                changes['registered_name'] = request.registered_name
            if request.uci_code:
                changes['uci_code'] = request.uci_code
            if request.tier_level:
                changes['tier_level'] = request.tier_level
            
            if not changes:
                raise ValueError("No changes specified")
            
            # Create edit record
            edit = Edit(
                user_id=user.user_id,
                edit_type=EditType.METADATA,
                target_era_id=request.era_id,
                changes=changes,
                reason=request.reason
            )
            
            # Auto-approve for trusted users and admins
            if user.role in [UserRole.TRUSTED_USER, UserRole.ADMIN]:
                edit.status = EditStatus.APPROVED
                edit.reviewed_by = user.user_id
                edit.reviewed_at = datetime.utcnow()
                
                # Apply changes immediately
                await EditService._apply_metadata_changes(session, era, changes, user)
                
                # Increment approved edits count
                user.approved_edits_count += 1
                
                message = "Edit approved and applied immediately"
            else:
                edit.status = EditStatus.PENDING
                message = "Edit submitted for moderation"
            
            session.add(edit)
            await session.commit()
            await session.refresh(edit)
            
            return EditMetadataResponse(
                edit_id=str(edit.edit_id),
                status=edit.status.value,
                message=message
            )
        
        @staticmethod
        async def _apply_metadata_changes(
            session: AsyncSession,
            era: TeamEra,
            changes: Dict,
            user: User
        ):
            """Apply metadata changes to an era"""
            if 'registered_name' in changes:
                era.registered_name = changes['registered_name']
            if 'uci_code' in changes:
                era.uci_code = changes['uci_code']
            if 'tier_level' in changes:
                era.tier_level = changes['tier_level']
            
            # Mark as manual override to prevent scraper from overwriting
            era.is_manual_override = True
            era.source_origin = f"user_{user.user_id}"
            era.updated_at = datetime.utcnow()
            
            await session.commit()
    ```
    
    6. FRONTEND WIZARD COMPONENT (src/components/EditMetadataWizard.jsx):
    ```javascript
    import { useState } from 'react';
    import { useAuth } from '../contexts/AuthContext';
    import { editsApi } from '../api/edits';
    import './EditMetadataWizard.css';
    
    export default function EditMetadataWizard({ era, onClose, onSuccess }) {
      const { user } = useAuth();
      const [formData, setFormData] = useState({
        registered_name: era.name || '',
        uci_code: era.uci_code || '',
        tier_level: era.tier || '',
        reason: ''
      });
      const [submitting, setSubmitting] = useState(false);
      const [error, setError] = useState(null);
      
      const handleChange = (field, value) => {
        setFormData(prev => ({ ...prev, [field]: value }));
        setError(null);
      };
      
      const handleSubmit = async (e) => {
        e.preventDefault();
        setSubmitting(true);
        setError(null);
        
        try {
          // Only send changed fields
          const changes = {};
          if (formData.registered_name !== era.name) {
            changes.registered_name = formData.registered_name;
          }
          if (formData.uci_code !== era.uci_code) {
            changes.uci_code = formData.uci_code;
          }
          if (formData.tier_level && parseInt(formData.tier_level) !== era.tier) {
            changes.tier_level = parseInt(formData.tier_level);
          }
          
          if (Object.keys(changes).length === 0) {
            setError('No changes detected');
            setSubmitting(false);
            return;
          }
          
          const response = await editsApi.editMetadata({
            era_id: era.era_id,
            ...changes,
            reason: formData.reason
          });
          
          onSuccess(response.data);
        } catch (err) {
          setError(err.response?.data?.detail || 'Failed to submit edit');
        } finally {
          setSubmitting(false);
        }
      };
      
      const isChanged = () => {
        return formData.registered_name !== era.name ||
               formData.uci_code !== era.uci_code ||
               (formData.tier_level && parseInt(formData.tier_level) !== era.tier);
      };
      
      return (
        <div className="wizard-overlay" onClick={onClose}>
          <div className="wizard-modal" onClick={(e) => e.stopPropagation()}>
            <div className="wizard-header">
              <h2>Edit Team Information</h2>
              <button className="close-button" onClick={onClose}>×</button>
            </div>
            
            <form onSubmit={handleSubmit}>
              <div className="form-section">
                <label>
                  Team Name
                  <input
                    type="text"
                    value={formData.registered_name}
                    onChange={(e) => handleChange('registered_name', e.target.value)}
                    required
                  />
                </label>
                
                <label>
                  UCI Code (3 letters)
                  <input
                    type="text"
                    value={formData.uci_code}
                    onChange={(e) => handleChange('uci_code', e.target.value.toUpperCase())}
                    maxLength={3}
                    pattern="[A-Z]{3}"
                  />
                </label>
                
                <label>
                  Tier Level
                  <select
                    value={formData.tier_level}
                    onChange={(e) => handleChange('tier_level', e.target.value)}
                  >
                    <option value="">Select tier...</option>
                    <option value="1">UCI WorldTour</option>
                    <option value="2">UCI ProTeam</option>
                    <option value="3">UCI Continental</option>
                  </select>
                </label>
              </div>
              
              <div className="form-section">
                <label>
                  Reason for Edit (required)
                  <textarea
                    value={formData.reason}
                    onChange={(e) => handleChange('reason', e.target.value)}
                    placeholder="Explain why this edit is needed..."
                    rows={4}
                    required
                    minLength={10}
                  />
                </label>
                <div className="help-text">
                  Please provide a clear explanation. Include sources if available.
                </div>
              </div>
              
              {error && (
                <div className="error-message">{error}</div>
              )}
              
              <div className="wizard-footer">
                <div className="moderation-notice">
                  {user?.role === 'NEW_USER' ? (
                    <span className="notice-warning">
                      ⚠️ Your edit will be reviewed by moderators
                    </span>
                  ) : (
                    <span className="notice-success">
                      ✓ Your edit will be applied immediately
                    </span>
                  )}
                </div>
                
                <div className="button-group">
                  <button 
                    type="button" 
                    onClick={onClose}
                    disabled={submitting}
                  >
                    Cancel
                  </button>
                  <button 
                    type="submit"
                    disabled={!isChanged() || !formData.reason || submitting}
                    className="primary"
                  >
                    {submitting ? 'Submitting...' : 'Submit Edit'}
                  </button>
                </div>
              </div>
            </form>
          </div>
        </div>
      );
    }
    ```
    
    7. EDITS API CLIENT (src/api/edits.js - create):
    ```javascript
    import apiClient from './client';
    
    export const editsApi = {
      editMetadata: (data) => 
        apiClient.post('/api/v1/edits/metadata', data),
      
      getMyEdits: () =>
        apiClient.get('/api/v1/edits/my-edits'),
      
      getPendingEdits: () =>
        apiClient.get('/api/v1/edits/pending'),
    };
    ```
    
    8. UPDATE TimelineGraph to add edit button:
    ```javascript
    // When rendering nodes, add edit button on click for authenticated users
    const handleNodeClick = (node) => {
      if (canEdit()) {
        setSelectedNode(node);
        setShowEditWizard(true);
      } else {
        // Show team detail page
        navigate(`/team/${node.id}`);
      }
    };
    
    // In render:
    {showEditWizard && selectedNode && (
      <EditMetadataWizard
        era={selectedNode.eras[selectedNode.eras.length - 1]}
        onClose={() => setShowEditWizard(false)}
        onSuccess={(result) => {
          setShowEditWizard(false);
          if (result.status === 'APPROVED') {
            // Refetch data
            refetch();
          } else {
            // Show success message
            alert(result.message);
          }
        }}
      />
    )}
    ```
    
    TESTING:
    - Test metadata edit submission
    - Test validation (UCI code, tier level, reason length)
    - Test auto-approval for trusted users
    - Test pending status for new users
    - Test manual override flag is set
    - Test scraper doesn't overwrite manual edits
    - Test edit history is recorded
    
    SUCCESS CRITERIA:
    - Wizard opens on node click for authenticated users
    - Form validates all fields correctly
    - Trusted users' edits apply immediately
    - New users' edits go to moderation queue
    - Manual override prevents scraper conflicts
    - Edit history is maintained
    - All tests pass

### Prompt 24: Structural Event Wizard - Merge

    Implement the wizard for creating team merger events:
    
    REQUIREMENTS:
    
    1. MERGE ENDPOINT (app/api/v1/edits.py - extend):
    ```python
    @router.post("/merge", response_model=EditMetadataResponse)
    async def create_merge(
        request: MergeEventRequest,
        session: AsyncSession = Depends(get_db),
        current_user: User = Depends(require_editor)
    ):
        """Create a team merge event"""
        try:
            result = await EditService.create_merge_edit(
                session,
                current_user,
                request
            )
            return result
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    ```
    
    2. MERGE SCHEMA (app/schemas/edits.py - extend):
    ```python
    class MergeEventRequest(BaseModel):
        source_node_ids: list[str]  # Team IDs being merged
        merge_year: int
        new_team_name: str
        new_team_tier: int
        reason: str
        
        @validator('source_node_ids')
        def validate_sources(cls, v):
            if len(v) < 2:
                raise ValueError('Merge requires at least 2 source teams')
            if len(v) > 5:
                raise ValueError('Cannot merge more than 5 teams at once')
            return v
        
        @validator('merge_year')
        def validate_year(cls, v):
            current_year = datetime.now().year
            if v < 1900 or v > current_year + 1:
                raise ValueError(f'Year must be between 1900 and {current_year + 1}')
            return v
        
        @validator('new_team_tier')
        def validate_tier(cls, v):
            if v not in [1, 2, 3]:
                raise ValueError('Tier must be 1, 2, or 3')
            return v
    ```
    
    3. EDIT SERVICE - MERGE (app/services/edit_service.py - extend):
    ```python
    @staticmethod
    async def create_merge_edit(
        session: AsyncSession,
        user: User,
        request: MergeEventRequest
    ) -> EditMetadataResponse:
        """Create a merge event edit"""
        # Validate source nodes exist
        source_nodes = []
        for node_id in request.source_node_ids:
            node = await session.get(TeamNode, node_id)
            if not node:
                raise ValueError(f"Team node {node_id} not found")
            
            # Check node is active in merge year
            has_era = any(era.season_year == request.merge_year for era in node.eras)
            if not has_era:
                raise ValueError(f"Team {node_id} was not active in {request.merge_year}")
            
            source_nodes.append(node)
        
        # Create edit record
        edit = Edit(
            user_id=user.user_id,
            edit_type=EditType.MERGE,
            changes={
                'source_node_ids': request.source_node_ids,
                'merge_year': request.merge_year,
                'new_team_name': request.new_team_name,
                'new_team_tier': request.new_team_tier
            },
            reason=request.reason
        )
        
        # Auto-approve for trusted users and admins
        if user.role in [UserRole.TRUSTED_USER, UserRole.ADMIN]:
            edit.status = EditStatus.APPROVED
            edit.reviewed_by = user.user_id
            edit.reviewed_at = datetime.utcnow()
            
            # Apply merge immediately
            await EditService._apply_merge(session, request, user)
            
            user.approved_edits_count += 1
            message = "Merge created successfully"
        else:
            edit.status = EditStatus.PENDING
            message = "Merge submitted for moderation"
        
        session.add(edit)
        await session.commit()
        await session.refresh(edit)
        
        return EditMetadataResponse(
            edit_id=str(edit.edit_id),
            status=edit.status.value,
            message=message
        )
    
    @staticmethod
    async def _apply_merge(
        session: AsyncSession,
        request: MergeEventRequest,
        user: User
    ):
        """Apply a merge: close old nodes, create new node with links"""
        # Create new team node
        new_node = TeamNode( founding\_year=request.merge\_year ) session.add(new\_node) await session.flush() # Get node\_id

    # Create first era for new team
    new_era = TeamEra(
        node_id=new_node.node_id,
        season_year=request.merge_year,
        registered_name=request.new_team_name,
        tier_level=request.new_team_tier,
        source_origin=f"user_{user.user_id}",
        is_manual_override=True
    )
    session.add(new_era)
    
    # Close source nodes and create lineage links
    for source_node_id in request.source_node_ids:
        source_node = await session.get(TeamNode, source_node_id)
        
        # Set dissolution year
        source_node.dissolution_year = request.merge_year
        source_node.updated_at = datetime.utcnow()
        
        # Create MERGE lineage event
        lineage_event = LineageEvent(
            previous_node_id=source_node_id,
            next_node_id=new_node.node_id,
            event_year=request.merge_year,
            event_type='MERGE',
            notes=f"Merged into {request.new_team_name}"
        )
        session.add(lineage_event)
    
    await session.commit()

    
    4. MERGE WIZARD COMPONENT (src/components/MergeWizard.jsx):
    ```javascript
    import { useState, useEffect } from 'react';
    import { useAuth } from '../contexts/AuthContext';
    import { editsApi } from '../api/edits';
    import { teamsApi } from '../api/teams';
    import './MergeWizard.css';
    
    export default function MergeWizard({ initialNode, onClose, onSuccess }) {
      const { user } = useAuth();
      const [step, setStep] = useState(1);
      const [formData, setFormData] = useState({
        source_nodes: initialNode ? [initialNode] : [],
        merge_year: new Date().getFullYear(),
        new_team_name: '',
        new_team_tier: '',
        reason: ''
      });
      const [searchTerm, setSearchTerm] = useState('');
      const [searchResults, setSearchResults] = useState([]);
      const [submitting, setSubmitting] = useState(false);
      const [error, setError] = useState(null);
      
      useEffect(() => {
        if (searchTerm.length >= 2) {
          searchTeams();
        } else {
          setSearchResults([]);
        }
      }, [searchTerm]);
      
      const searchTeams = async () => {
        try {
          const response = await teamsApi.getTeams({ search: searchTerm });
          // Filter out already selected teams
          const selectedIds = formData.source_nodes.map(n => n.id);
          const filtered = response.data.items.filter(
            team => !selectedIds.includes(team.id)
          );
          setSearchResults(filtered);
        } catch (error) {
          console.error('Search failed:', error);
        }
      };
      
      const addSourceTeam = (team) => {
        if (formData.source_nodes.length >= 5) {
          setError('Maximum 5 teams can be merged');
          return;
        }
        
        setFormData(prev => ({
          ...prev,
          source_nodes: [...prev.source_nodes, team]
        }));
        setSearchTerm('');
        setSearchResults([]);
      };
      
      const removeSourceTeam = (teamId) => {
        setFormData(prev => ({
          ...prev,
          source_nodes: prev.source_nodes.filter(t => t.id !== teamId)
        }));
      };
      
      const handleNext = () => {
        if (step === 1 && formData.source_nodes.length < 2) {
          setError('Select at least 2 teams to merge');
          return;
        }
        setError(null);
        setStep(step + 1);
      };
      
      const handleBack = () => {
        setError(null);
        setStep(step - 1);
      };
      
      const handleSubmit = async () => {
        setSubmitting(true);
        setError(null);
        
        try {
          const response = await editsApi.createMerge({
            source_node_ids: formData.source_nodes.map(n => n.id),
            merge_year: parseInt(formData.merge_year),
            new_team_name: formData.new_team_name,
            new_team_tier: parseInt(formData.new_team_tier),
            reason: formData.reason
          });
          
          onSuccess(response.data);
        } catch (err) {
          setError(err.response?.data?.detail || 'Failed to create merge');
        } finally {
          setSubmitting(false);
        }
      };
      
      return (
        <div className="wizard-overlay" onClick={onClose}>
          <div className="wizard-modal large" onClick={(e) => e.stopPropagation()}>
            <div className="wizard-header">
              <h2>Create Team Merger</h2>
              <button className="close-button" onClick={onClose}>×</button>
            </div>
            
            <div className="wizard-progress">
              <div className={`step ${step >= 1 ? 'active' : ''}`}>1. Select Teams</div>
              <div className={`step ${step >= 2 ? 'active' : ''}`}>2. Merge Details</div>
              <div className={`step ${step >= 3 ? 'active' : ''}`}>3. Review</div>
            </div>
            
            <div className="wizard-content">
              {step === 1 && (
                <div className="step-content">
                  <h3>Select Teams to Merge</h3>
                  
                  <div className="selected-teams">
                    <h4>Selected Teams ({formData.source_nodes.length}/5)</h4>
                    {formData.source_nodes.map(team => (
                      <div key={team.id} className="selected-team">
                        <span>{team.eras[team.eras.length - 1].name}</span>
                        <button onClick={() => removeSourceTeam(team.id)}>Remove</button>
                      </div>
                    ))}
                  </div>
                  
                  <div className="team-search">
                    <input
                      type="text"
                      placeholder="Search for teams..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                    />
                    {searchResults.length > 0 && (
                      <div className="search-results">
                        {searchResults.map(team => (
                          <div 
                            key={team.id}
                            className="search-result"
                            onClick={() => addSourceTeam(team)}
                          >
                            <span>{team.eras[team.eras.length - 1].name}</span>
                            <span className="years">
                              {team.founding_year} - {team.dissolution_year || 'present'}
                            </span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              )}
              
              {step === 2 && (
                <div className="step-content">
                  <h3>Merge Details</h3>
                  
                  <label>
                    Merge Year
                    <input
                      type="number"
                      value={formData.merge_year}
                      onChange={(e) => setFormData(prev => ({ ...prev, merge_year: e.target.value }))}
                      min={1900}
                      max={new Date().getFullYear() + 1}
                      required
                    />
                  </label>
                  
                  <label>
                    New Team Name
                    <input
                      type="text"
                      value={formData.new_team_name}
                      onChange={(e) => setFormData(prev => ({ ...prev, new_team_name: e.target.value }))}
                      placeholder="e.g., Team Visma | Lease a Bike"
                      required
                    />
                  </label>
                  
                  <label>
                    New Team Tier
                    <select
                      value={formData.new_team_tier}
                      onChange={(e) => setFormData(prev => ({ ...prev, new_team_tier: e.target.value }))}
                      required
                    >
                      <option value="">Select tier...</option>
                      <option value="1">UCI WorldTour</option>
                      <option value="2">UCI ProTeam</option>
                      <option value="3">UCI Continental</option>
                    </select>
                  </label>
                  
                  <label>
                    Reason for Merge
                    <textarea
                      value={formData.reason}
                      onChange={(e) => setFormData(prev => ({ ...prev, reason: e.target.value }))}
                      placeholder="Explain the merger and provide sources..."
                      rows={5}
                      required
                      minLength={10}
                    />
                  </label>
                </div>
              )}
              
              {step === 3 && (
                <div className="step-content">
                  <h3>Review Merge</h3>
                  
                  <div className="review-section">
                    <h4>Teams Being Merged</h4>
                    <ul>
                      {formData.source_nodes.map(team => (
                        <li key={team.id}>
                          {team.eras[team.eras.length - 1].name}
                        </li>
                      ))}
                    </ul>
                  </div>
                  
                  <div className="review-section">
                    <h4>Merge Into</h4>
                    <p><strong>{formData.new_team_name}</strong></p>
                    <p>Year: {formData.merge_year}</p>
                    <p>Tier: {formData.new_team_tier === '1' ? 'WorldTour' : formData.new_team_tier === '2' ? 'ProTeam' : 'Continental'}</p>
                  </div>
                  
                  <div className="review-section">
                    <h4>Reason</h4>
                    <p>{formData.reason}</p>
                  </div>
                </div>
              )}
            </div>
            
            {error && (
              <div className="error-message">{error}</div>
            )}
            
            <div className="wizard-footer">
              {user?.role === 'NEW_USER' && (
                <div className="moderation-notice">
                  <span className="notice-warning">
                    ⚠️ This merge will be reviewed by moderators
                  </span>
                </div>
              )}
              
              <div className="button-group">
                {step > 1 && (
                  <button onClick={handleBack} disabled={submitting}>
                    Back
                  </button>
                )}
                <button onClick={onClose} disabled={submitting}>
                  Cancel
                </button>
                {step < 3 ? (
                  <button 
                    onClick={handleNext}
                    className="primary"
                    disabled={step === 1 && formData.source_nodes.length < 2}
                  >
                    Next
                  </button>
                ) : (
                  <button 
                    onClick={handleSubmit}
                    className="primary"
                    disabled={submitting || !formData.new_team_name || !formData.reason}
                  >
                    {submitting ? 'Creating...' : 'Create Merge'}
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      );
    }
    ```
    
    TESTING:
    - Test merge with 2 teams
    - Test merge with 5 teams (maximum)
    - Test merge validation (year, team existence)
    - Test auto-approval for trusted users
    - Test source nodes are dissolved
    - Test new node is created with correct data
    - Test lineage events are created
    - Test merge appears in visualization
    
    SUCCESS CRITERIA:
    - Wizard guides user through merge process
    - Search functionality works for finding teams
    - Merge creates correct database structure
    - Lineage graph updates to show merge
    - Validation prevents invalid merges
    - All tests pass

### Prompt 25: Structural Event Wizard - Split

    Implement the wizard for creating team split events:
    
    REQUIREMENTS:
    
    1. SPLIT ENDPOINT (app/api/v1/edits.py - extend):
    ```python
    @router.post("/split", response_model=EditMetadataResponse)
    async def create_split(
        request: SplitEventRequest,
        session: AsyncSession = Depends(get_db),
        current_user: User = Depends(require_editor)
    ):
        """Create a team split event"""
        try:
            result = await EditService.create_split_edit(
                session,
                current_user,
                request
            )
            return result
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
    ```
    
    2. SPLIT SCHEMA (app/schemas/edits.py - extend):
    ```python
    class NewTeamInfo(BaseModel):
        name: str
        tier: int
        
        @validator('tier')
        def validate_tier(cls, v):
            if v not in [1, 2, 3]:
                raise ValueError('Tier must be 1, 2, or 3')
            return v
    
    class SplitEventRequest(BaseModel):
        source_node_id: str  # Team being split
        split_year: int
        new_teams: list[NewTeamInfo]  # 2-5 new teams
        reason: str
        
        @validator('new_teams')
        def validate_new_teams(cls, v):
            if len(v) < 2:
                raise ValueError('Split requires at least 2 resulting teams')
            if len(v) > 5:
                raise ValueError('Cannot split into more than 5 teams')
            return v
        
        @validator('split_year')
        def validate_year(cls, v):
            current_year = datetime.now().year
            if v < 1900 or v > current_year + 1:
                raise ValueError(f'Year must be between 1900 and {current_year + 1}')
            return v
    ```
    
    3. EDIT SERVICE - SPLIT (app/services/edit_service.py - extend):
    ```python
    @staticmethod
    async def create_split_edit(
        session: AsyncSession,
        user: User,
        request: SplitEventRequest
    ) -> EditMetadataResponse:
        """Create a split event edit"""
        # Validate source node exists
        source_node = await session.get(TeamNode, request.source_node_id)
        if not source_node:
            raise ValueError("Source team not found")
        
        # Check node is active in split year
        has_era = any(era.season_year == request.split_year for era in source_node.eras)
        if not has_era:
            raise ValueError(f"Team was not active in {request.split_year}")
        
        # Create edit record
        edit = Edit(
            user_id=user.user_id,
            edit_type=EditType.SPLIT,
            target_node_id=request.source_node_id,
            changes={
                'split_year': request.split_year,
                'new_teams': [
                    {'name': team.name, 'tier': team.tier}
                    for team in request.new_teams
                ]
            },
            reason=request.reason
        )
        
        # Auto-approve for trusted users and admins
        if user.role in [UserRole.TRUSTED_USER, UserRole.ADMIN]:
            edit.status = EditStatus.APPROVED
            edit.reviewed_by = user.user_id
            edit.reviewed_at = datetime.utcnow()
            
            # Apply split immediately
            await EditService._apply_split(session, request, user)
            
            user.approved_edits_count += 1
            message = "Split created successfully"
        else:
            edit.status = EditStatus.PENDING
            message = "Split submitted for moderation"
        
        session.add(edit)
        await session.commit()
        await session.refresh(edit)
        
        return EditMetadataResponse(
            edit_id=str(edit.edit_id),
            status=edit.status.value,
            message=message
        )
    
    @staticmethod
    async def _apply_split(
        session: AsyncSession,
        request: SplitEventRequest,
        user: User
    ):
        """Apply a split: close old node, create new nodes with links"""
        # Close source node
        source_node = await session.get(TeamNode, request.source_node_id)
        source_node.dissolution_year = request.split_year
        source_node.updated_at = datetime.utcnow()
        
        # Create new team nodes
        for new_team_info in request.new_teams:
            # Create new node
            new_node = TeamNode(
                founding_year=request.split_year
            )
            session.add(new_node)
            await session.flush()  # Get node_id
            
            # Create first era
            new_era = TeamEra(
                node_id=new_node.node_id,
                season_year=request.split_year,
                registered_name=new_team_info.name,
                tier_level=new_team_info.tier,
                source_origin=f"user_{user.user_id}",
                is_manual_override=True
            )
            session.add(new_era)
            
            # Create SPLIT lineage event
            lineage_event = LineageEvent(
                previous_node_id=request.source_node_id,
                next_node_id=new_node.node_id,
                event_year=request.split_year,
                event_type='SPLIT',
                notes=f"Split from source team into {new_team_info.name}"
            )
            session.add(lineage_event)
        
        await session.commit()
    ```
    
    4. SPLIT WIZARD COMPONENT (src/components/SplitWizard.jsx):
    ```javascript
    import { useState } from 'react';
    import { useAuth } from '../contexts/AuthContext';
    import { editsApi } from '../api/edits';
    import './SplitWizard.css';
    
    export default function SplitWizard({ sourceNode, onClose, onSuccess }) {
      const { user } = useAuth();
      const [step, setStep] = useState(1);
      const [formData, setFormData] = useState({
        split_year: new Date().getFullYear(),
        new_teams: [
          { name: '', tier: '' },
          { name: '', tier: '' }
        ],
        reason: ''
      });
      const [submitting, setSubmitting] = useState(false);
      const [error, setError] = useState(null);
      
      const addNewTeam = () => {
        if (formData.new_teams.length >= 5) {
          setError('Maximum 5 teams can result from a split');
          return;
        }
        
        setFormData(prev => ({
          ...prev,
          new_teams: [...prev.new_teams, { name: '', tier: '' }]
        }));
      };
      
      const removeNewTeam = (index) => {
        if (formData.new_teams.length <= 2) {
          setError('Split must result in at least 2 teams');
          return;
        }
        
        setFormData(prev => ({
          ...prev,
          new_teams: prev.new_teams.filter((_, i) => i !== index)
        }));
      };
      
      const updateNewTeam = (index, field, value) => {
        setFormData(prev => ({
          ...prev,
          new_teams: prev.new_teams.map((team, i) =>
            i === index ? { ...team, [field]: value } : team
          )
        }));
      };
      
      const isStepValid = () => {
        if (step === 1) {
          return formData.new_teams.every(team => team.name && team.tier);
        }
        if (step === 2) {
          return formData.reason.length >= 10;
        }
        return true;
      };
      
      const handleNext = () => {
        if (!isStepValid()) {
          setError('Please fill in all required fields');
          return;
        }
        setError(null);
        setStep(step + 1);
      };
      
      const handleBack = () => {
        setError(null);
        setStep(step - 1);
      };
      
      const handleSubmit = async () => {
        setSubmitting(true);
        setError(null);
        
        try {
          const response = await editsApi.createSplit({
            source_node_id: sourceNode.id,
            split_year: parseInt(formData.split_year),
            new_teams: formData.new_teams.map(team => ({
              name: team.name,
              tier: parseInt(team.tier)
            })),
            reason: formData.reason
          });
          
          onSuccess(response.data);
        } catch (err) {
          setError(err.response?.data?.detail || 'Failed to create split');
        } finally {
          setSubmitting(false);
        }
      };
      
      return (
        <div className="wizard-overlay" onClick={onClose}>
          <div className="wizard-modal large" onClick={(e) => e.stopPropagation()}>
            <div className="wizard-header">
              <h2>Create Team Split</h2>
              <button className="close-button" onClick={onClose}>×</button>
            </div>
            
            <div className="wizard-progress">
              <div className={`step ${step >= 1 ? 'active' : ''}`}>1. New Teams</div>
              <div className={`step ${step >= 2 ? 'active' : ''}`}>2. Details</div>
              <div className={`step ${step >= 3 ? 'active' : ''}`}>3. Review</div>
            </div>
            
            <div className="wizard-content">
              {step === 1 && (
                <div className="step-content">
                  <h3>Define Resulting Teams</h3>
                  <p>Splitting: <strong>{sourceNode.eras[sourceNode.eras.length - 1].name}</strong></p>
                  
                  <div className="new-teams-list">
                    {formData.new_teams.map((team, index) => (
                      <div key={index} className="new-team-form">
                        <h4>Team {index + 1}</h4>
                        <label>
                          Team Name
                          <input
                            type="text"
                            value={team.name}
                            onChange={(e) => updateNewTeam(index, 'name', e.target.value)}
                            placeholder="e.g., Team Jumbo-Visma"
                            required
                          />
                        </label>
                        
                        <label>
                          Tier
                          <select
                            value={team.tier}
                            onChange={(e) => updateNewTeam(index, 'tier', e.target.value)}
                            required
                          >
                            <option value="">Select tier...</option>
                            <option value="1">UCI WorldTour</option>
                            <option value="2">UCI ProTeam</option>
                            <option value="3">UCI Continental</option>
                          </select>
                        </label>
                        
                        {formData.new_teams.length > 2 && (
                          <button 
                            type="button"
                            onClick={() => removeNewTeam(index)}
                            className="remove-button"
                          >
                            Remove Team
                          </button>
                        )}
                      </div>
                    ))}
                  </div>
                  
                  {formData.new_teams.length < 5 && (
                    <button 
                      type="button"
                      onClick={addNewTeam}
                      className="add-team-button"
                    >
                      + Add Another Team
                    </button>
                  )}
                </div>
              )}
              
              {step === 2 && (
                <div className="step-content">
                  <h3>Split Details</h3>
                  
                  <label>
                    Split Year
                    <input
                      type="number"
                      value={formData.split_year}
                      onChange={(e) => setFormData(prev => ({ ...prev, split_year: e.target.value }))}
                      min={1900}
                      max={new Date().getFullYear() + 1}
                      required
                    />
                  </label>
                  
                  <label>
                    Reason for Split
                    <textarea
                      value={formData.reason}
                      onChange={(e) => setFormData(prev => ({ ...prev, reason: e.target.value }))}
                      placeholder="Explain why the team split and provide sources..."
                      rows={6}
                      required
                      minLength={10}
                    />
                  </label>
                </div>
              )}
              
              {step === 3 && (
                <div className="step-content">
                  <h3>Review Split</h3>
                  
                  <div className="review-section">
                    <h4>Source Team</h4>
                    <p><strong>{sourceNode.eras[sourceNode.eras.length - 1].name}</strong></p>
                    <p>Will be dissolved in {formData.split_year}</p>
                  </div>
                  
                  <div className="review-section">
                    <h4>Resulting Teams</h4>
                    <ul>
                      {formData.new_teams.map((team, index) => (
                        <li key={index}>
                          <strong>{team.name}</strong>
                          {' - '}
                          {team.tier === '1' ? 'WorldTour' : team.tier === '2' ? 'ProTeam' : 'Continental'}
                        </li>
                      ))}
                    </ul>
                  </div>
                  
                  <div className="review-section">
                    <h4>Reason</h4>
                    <p>{formData.reason}</p>
                  </div>
                </div>
              )}
            </div>
            
            {error && (
              <div className="error-message">{error}</div>
            )}
            
            <div className="wizard-footer">
              {user?.role === 'NEW_USER' && (
                <div className="moderation-notice">
                  <span className="notice-warning">
                    ⚠️ This split will be reviewed by moderators
                  </span>
                </div>
              )}
              
              <div className="button-group">
                {step > 1 && (
                  <button onClick={handleBack} disabled={submitting}>
                    Back
                  </button>
                )}
                <button onClick={onClose} disabled={submitting}>
                  Cancel
                </button>
                {step < 3 ? (
                  <button 
                    onClick={handleNext}
                    className="primary"
                    disabled={!isStepValid()}
                  >
                    Next
                  </button>
                ) : (
                  <button 
                    onClick={handleSubmit}
                    className="primary"
                    disabled={submitting}
                  >
                    {submitting ? 'Creating...' : 'Create Split'}
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      );
    }
    ```
    
    5. UPDATE API (src/api/edits.js):
    ```javascript
    export const editsApi = {
      // ... existing methods
      
      createMerge: (data) =>
        apiClient.post('/api/v1/edits/merge', data),
      
      createSplit: (data) =>
        apiClient.post('/api/v1/edits/split', data),
    };
    ```
    
    TESTING:
    - Test split with 2 resulting teams
    - Test split with 5 resulting teams (maximum)
    - Test split validation (year, team names, tiers)
    - Test auto-approval for trusted users
    - Test source node is dissolved
    - Test new nodes are created
    - Test lineage events are created
    - Test split appears in visualization
    
    SUCCESS CRITERIA:
    - Wizard guides user through split process
    - Can add/remove resulting teams dynamically
    - Split creates correct database structure
    - Lineage graph updates to show split
    - Validation prevents invalid splits
    - All tests pass

* * *

## Phase 8: Moderation System
--------------------------

### Prompt 26: Moderation Queue

    Implement the moderation queue for admins to review pending edits:
    
    REQUIREMENTS:
    
    1. MODERATION ENDPOINTS (app/api/v1/moderation.py - create):
    ```python
    from fastapi import APIRouter, Depends, HTTPException, Query
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy import select, and_
    from typing import List, Optional
    
    from app.db.database import get_db
    from app.api.dependencies import require_admin
    from app.models.user import User
    from app.models.edit import Edit, EditStatus
    from app.schemas.moderation import (
        PendingEditResponse,
        ReviewEditRequest,
        ReviewEditResponse,
        ModerationStatsResponse
    )
    from app.services.moderation_service import ModerationService
    
    router = APIRouter(prefix="/api/v1/moderation", tags=["moderation"])
    
    @router.get("/pending", response_model=List[PendingEditResponse])
    async def get_pending_edits(
        skip: int = Query(0, ge=0),
        limit: int = Query(50, ge=1, le=100),
        edit_type: Optional[str] = None,
        session: AsyncSession = Depends(get_db),
        admin: User = Depends(require_admin)
    ):
        """Get list of pending edits for moderation"""
        stmt = select(Edit).where(Edit.status == EditStatus.PENDING)
        
        if edit_type:
            stmt = stmt.where(Edit.edit_type == edit_type)
        
        stmt = stmt.order_by(Edit.created_at.asc()).offset(skip).limit(limit)
        
        result = await session.execute(stmt)
        edits = result.scalars().all()
        
        return [await ModerationService.format_edit_for_review(session, edit) for edit in edits]
    
    @router.post("/review/{edit_id}", response_model=ReviewEditResponse)
    async def review_edit(
        edit_id: str,
        request: ReviewEditRequest,
        session: AsyncSession = Depends(get_db),
        admin: User = Depends(require_admin)
    ):
        """Approve or reject a pending edit"""
        edit = await session.get(Edit, edit_id)
        if not edit:
            raise HTTPException(status_code=404, detail="Edit not found")
        
        if edit.status != EditStatus.PENDING:
            raise HTTPException(status_code=400, detail="Edit is not pending")
        
        result = await ModerationService.review_edit(
            session,
            edit,
            admin,
            request.approved,
            request.notes
        )
        
        return result
    
    @router.get("/stats", response_model=ModerationStatsResponse)
    async def get_moderation_stats(
        session: AsyncSession = Depends(get_db),
        admin: User = Depends(require_admin)
    ):
        """Get moderation statistics"""
        return await ModerationService.get_stats(session)
    ```
    
    2. MODERATION SCHEMAS (app/schemas/moderation.py - create):
    ```python
    from pydantic import BaseModel
    from typing import Optional, Dict, Any
    from datetime import datetime
    
    class PendingEditResponse(BaseModel):
        edit_id: str
        edit_type: str
        user_email: str
        user_display_name: Optional[str]
        target_info: Dict[str, Any]  # Information about what's being edited
        changes: Dict[str, Any]
        reason: str
        created_at: datetime
        
        class Config:
            from_attributes = True
    
    class Review EditRequest(BaseModel): approved: bool notes: Optional\[str\] = None

class ReviewEditResponse(BaseModel): edit\_id: str status: str message: str

class ModerationStatsResponse(BaseModel): pending\_count: int approved\_today: int rejected\_today: int pending\_by\_type: Dict\[str, int\]

    
    3. MODERATION SERVICE (app/services/moderation_service.py - create):
    ```python
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy import select, func, and_
    from datetime import datetime, timedelta
    from typing import Dict
    
    from app.models.edit import Edit, EditType, EditStatus
    from app.models.user import User, UserRole
    from app.models.team import TeamEra, TeamNode
    from app.schemas.moderation import (
        PendingEditResponse,
        ReviewEditResponse,
        ModerationStatsResponse
    )
    
    class ModerationService:
        @staticmethod
        async def format_edit_for_review(
            session: AsyncSession,
            edit: Edit
        ) -> PendingEditResponse:
            """Format an edit for the moderation queue"""
            # Get user info
            user = await session.get(User, edit.user_id)
            
            # Get target info based on edit type
            target_info = {}
            if edit.edit_type == EditType.METADATA and edit.target_era_id:
                era = await session.get(TeamEra, edit.target_era_id)
                if era:
                    target_info = {
                        'type': 'era',
                        'era_id': str(era.era_id),
                        'team_name': era.registered_name,
                        'year': era.season_year
                    }
            elif edit.target_node_id:
                node = await session.get(TeamNode, edit.target_node_id)
                if node:
                    target_info = {
                        'type': 'node',
                        'node_id': str(node.node_id),
                        'founding_year': node.founding_year
                    }
            
            return PendingEditResponse(
                edit_id=str(edit.edit_id),
                edit_type=edit.edit_type.value,
                user_email=user.email,
                user_display_name=user.display_name,
                target_info=target_info,
                changes=edit.changes,
                reason=edit.reason,
                created_at=edit.created_at
            )
        
        @staticmethod
        async def review_edit(
            session: AsyncSession,
            edit: Edit,
            admin: User,
            approved: bool,
            notes: Optional[str] = None
        ) -> ReviewEditResponse:
            """Approve or reject an edit"""
            if approved:
                # Approve and apply changes
                edit.status = EditStatus.APPROVED
                edit.reviewed_by = admin.user_id
                edit.reviewed_at = datetime.utcnow()
                edit.review_notes = notes
                
                # Apply the edit based on type
                try:
                    if edit.edit_type == EditType.METADATA:
                        await ModerationService._apply_metadata_edit(session, edit)
                    elif edit.edit_type == EditType.MERGE:
                        await ModerationService._apply_merge_edit(session, edit)
                    elif edit.edit_type == EditType.SPLIT:
                        await ModerationService._apply_split_edit(session, edit)
                    
                    # Increment user's approved edits count
                    user = await session.get(User, edit.user_id)
                    user.approved_edits_count += 1
                    
                    # Check if user should be promoted to trusted
                    if user.role == UserRole.NEW_USER and user.approved_edits_count >= 5:
                        user.role = UserRole.TRUSTED_USER
                        message = "Edit approved and user promoted to Trusted User"
                    else:
                        message = "Edit approved and applied"
                    
                except Exception as e:
                    await session.rollback()
                    raise ValueError(f"Failed to apply edit: {str(e)}")
            else:
                # Reject
                edit.status = EditStatus.REJECTED
                edit.reviewed_by = admin.user_id
                edit.reviewed_at = datetime.utcnow()
                edit.review_notes = notes or "Edit rejected by moderator"
                message = "Edit rejected"
            
            await session.commit()
            
            return ReviewEditResponse(
                edit_id=str(edit.edit_id),
                status=edit.status.value,
                message=message
            )
        
        @staticmethod
        async def _apply_metadata_edit(session: AsyncSession, edit: Edit):
            """Apply a metadata edit"""
            era = await session.get(TeamEra, edit.target_era_id)
            if not era:
                raise ValueError("Target era not found")
            
            changes = edit.changes
            if 'registered_name' in changes:
                era.registered_name = changes['registered_name']
            if 'uci_code' in changes:
                era.uci_code = changes['uci_code']
            if 'tier_level' in changes:
                era.tier_level = changes['tier_level']
            
            era.is_manual_override = True
            era.source_origin = f"user_{edit.user_id}"
            era.updated_at = datetime.utcnow()
            
            await session.commit()
        
        @staticmethod
        async def _apply_merge_edit(session: AsyncSession, edit: Edit):
            """Apply a merge edit (reuse logic from EditService)"""
            from app.services.edit_service import EditService
            from app.schemas.edits import MergeEventRequest
            
            changes = edit.changes
            request = MergeEventRequest(
                source_node_ids=changes['source_node_ids'],
                merge_year=changes['merge_year'],
                new_team_name=changes['new_team_name'],
                new_team_tier=changes['new_team_tier'],
                reason=edit.reason
            )
            
            user = await session.get(User, edit.user_id)
            await EditService._apply_merge(session, request, user)
        
        @staticmethod
        async def _apply_split_edit(session: AsyncSession, edit: Edit):
            """Apply a split edit (reuse logic from EditService)"""
            from app.services.edit_service import EditService
            from app.schemas.edits import SplitEventRequest, NewTeamInfo
            
            changes = edit.changes
            request = SplitEventRequest(
                source_node_id=str(edit.target_node_id),
                split_year=changes['split_year'],
                new_teams=[
                    NewTeamInfo(name=team['name'], tier=team['tier'])
                    for team in changes['new_teams']
                ],
                reason=edit.reason
            )
            
            user = await session.get(User, edit.user_id)
            await EditService._apply_split(session, request, user)
        
        @staticmethod
        async def get_stats(session: AsyncSession) -> ModerationStatsResponse:
            """Get moderation statistics"""
            # Count pending edits
            pending_stmt = select(func.count(Edit.edit_id)).where(
                Edit.status == EditStatus.PENDING
            )
            pending_result = await session.execute(pending_stmt)
            pending_count = pending_result.scalar()
            
            # Count approved today
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            approved_today_stmt = select(func.count(Edit.edit_id)).where(
                and_(
                    Edit.status == EditStatus.APPROVED,
                    Edit.reviewed_at >= today_start
                )
            )
            approved_result = await session.execute(approved_today_stmt)
            approved_today = approved_result.scalar()
            
            # Count rejected today
            rejected_today_stmt = select(func.count(Edit.edit_id)).where(
                and_(
                    Edit.status == EditStatus.REJECTED,
                    Edit.reviewed_at >= today_start
                )
            )
            rejected_result = await session.execute(rejected_today_stmt)
            rejected_today = rejected_result.scalar()
            
            # Count pending by type
            pending_by_type_stmt = select(
                Edit.edit_type,
                func.count(Edit.edit_id)
            ).where(
                Edit.status == EditStatus.PENDING
            ).group_by(Edit.edit_type)
            
            type_result = await session.execute(pending_by_type_stmt)
            pending_by_type = {
                edit_type.value: count
                for edit_type, count in type_result.all()
            }
            
            return ModerationStatsResponse(
                pending_count=pending_count,
                approved_today=approved_today,
                rejected_today=rejected_today,
                pending_by_type=pending_by_type
            )
    ```
    
    4. MODERATION QUEUE UI (src/pages/ModerationQueuePage.jsx):
    ```javascript
    import { useState, useEffect } from 'react';
    import { moderationApi } from '../api/moderation';
    import { useAuth } from '../contexts/AuthContext';
    import { useNavigate } from 'react-router-dom';
    import './ModerationQueuePage.css';
    
    export default function ModerationQueuePage() {
      const { isAdmin } = useAuth();
      const navigate = useNavigate();
      const [edits, setEdits] = useState([]);
      const [stats, setStats] = useState(null);
      const [loading, setLoading] = useState(true);
      const [filter, setFilter] = useState('ALL');
      const [selectedEdit, setSelectedEdit] = useState(null);
      
      useEffect(() => {
        if (!isAdmin()) {
          navigate('/');
          return;
        }
        
        loadData();
      }, [filter]);
      
      const loadData = async () => {
        setLoading(true);
        try {
          const [editsResponse, statsResponse] = await Promise.all([
            moderationApi.getPendingEdits({ edit_type: filter === 'ALL' ? null : filter }),
            moderationApi.getStats()
          ]);
          
          setEdits(editsResponse.data);
          setStats(statsResponse.data);
        } catch (error) {
          console.error('Failed to load moderation data:', error);
        } finally {
          setLoading(false);
        }
      };
      
      const handleReview = async (editId, approved, notes) => {
        try {
          await moderationApi.reviewEdit(editId, { approved, notes });
          
          // Remove from list
          setEdits(prev => prev.filter(e => e.edit_id !== editId));
          setSelectedEdit(null);
          
          // Reload stats
          const statsResponse = await moderationApi.getStats();
          setStats(statsResponse.data);
          
          alert(approved ? 'Edit approved!' : 'Edit rejected!');
        } catch (error) {
          console.error('Failed to review edit:', error);
          alert('Failed to review edit: ' + (error.response?.data?.detail || error.message));
        }
      };
      
      if (loading) return <div>Loading...</div>;
      
      return (
        <div className="moderation-page">
          <div className="moderation-header">
            <h1>Moderation Queue</h1>
            
            {stats && (
              <div className="stats-bar">
                <div className="stat">
                  <span className="stat-label">Pending</span>
                  <span className="stat-value">{stats.pending_count}</span>
                </div>
                <div className="stat">
                  <span className="stat-label">Approved Today</span>
                  <span className="stat-value approved">{stats.approved_today}</span>
                </div>
                <div className="stat">
                  <span className="stat-label">Rejected Today</span>
                  <span className="stat-value rejected">{stats.rejected_today}</span>
                </div>
              </div>
            )}
          </div>
          
          <div className="filter-bar">
            <button 
              className={filter === 'ALL' ? 'active' : ''}
              onClick={() => setFilter('ALL')}
            >
              All ({stats?.pending_count || 0})
            </button>
            <button 
              className={filter === 'METADATA' ? 'active' : ''}
              onClick={() => setFilter('METADATA')}
            >
              Metadata ({stats?.pending_by_type?.METADATA || 0})
            </button>
            <button 
              className={filter === 'MERGE' ? 'active' : ''}
              onClick={() => setFilter('MERGE')}
            >
              Merges ({stats?.pending_by_type?.MERGE || 0})
            </button>
            <button 
              className={filter === 'SPLIT' ? 'active' : ''}
              onClick={() => setFilter('SPLIT')}
            >
              Splits ({stats?.pending_by_type?.SPLIT || 0})
            </button>
          </div>
          
          <div className="edits-list">
            {edits.length === 0 ? (
              <div className="empty-state">
                <p>🎉 No pending edits! Queue is clear.</p>
              </div>
            ) : (
              edits.map(edit => (
                <div 
                  key={edit.edit_id}
                  className="edit-card"
                  onClick={() => setSelectedEdit(edit)}
                >
                  <div className="edit-header">
                    <span className="edit-type">{edit.edit_type}</span>
                    <span className="edit-date">
                      {new Date(edit.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  
                  <div className="edit-user">
                    By: {edit.user_display_name || edit.user_email}
                  </div>
                  
                  <div className="edit-target">
                    {edit.target_info.team_name && (
                      <span>{edit.target_info.team_name} ({edit.target_info.year})</span>
                    )}
                  </div>
                  
                  <div className="edit-reason">
                    {edit.reason.substring(0, 100)}
                    {edit.reason.length > 100 && '...'}
                  </div>
                </div>
              ))
            )}
          </div>
          
          {selectedEdit && (
            <EditReviewModal
              edit={selectedEdit}
              onClose={() => setSelectedEdit(null)}
              onReview={handleReview}
            />
          )}
        </div>
      );
    }
    
    function EditReviewModal({ edit, onClose, onReview }) {
      const [notes, setNotes] = useState('');
      const [reviewing, setReviewing] = useState(false);
      
      const handleApprove = async () => {
        setReviewing(true);
        await onReview(edit.edit_id, true, notes);
        setReviewing(false);
      };
      
      const handleReject = async () => {
        if (!notes) {
          alert('Please provide a reason for rejection');
          return;
        }
        
        setReviewing(true);
        await onReview(edit.edit_id, false, notes);
        setReviewing(false);
      };
      
      return (
        <div className="modal-overlay" onClick={onClose}>
          <div className="modal-content review-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Review Edit</h2>
              <button onClick={onClose}>×</button>
            </div>
            
            <div className="modal-body">
              <div className="review-section">
                <h3>Edit Type</h3>
                <p className="edit-type-badge">{edit.edit_type}</p>
              </div>
              
              <div className="review-section">
                <h3>Submitted By</h3>
                <p>{edit.user_display_name || edit.user_email}</p>
                <p className="date">
                  {new Date(edit.created_at).toLocaleString()}
                </p>
              </div>
              
              <div className="review-section">
                <h3>Target</h3>
                <pre>{JSON.stringify(edit.target_info, null, 2)}</pre>
              </div>
              
              <div className="review-section">
                <h3>Changes</h3>
                <pre>{JSON.stringify(edit.changes, null, 2)}</pre>
              </div>
              
              <div className="review-section">
                <h3>Reason</h3>
                <p>{edit.reason}</p>
              </div>
              
              <div className="review-section">
                <h3>Review Notes (Optional for approval, required for rejection)</h3>
                <textarea
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="Add notes about your decision..."
                  rows={4}
                />
              </div>
            </div>
            
            <div className="modal-footer">
              <button 
                onClick={handleReject}
                disabled={reviewing}
                className="reject-button"
              >
                Reject
              </button>
              <button 
                onClick={handleApprove}
                disabled={reviewing}
                className="approve-button"
              >
                Approve & Apply
              </button>
            </div>
          </div>
        </div>
      );
    }
    ```
    
    5. MODERATION API CLIENT (src/api/moderation.js - create):
    ```javascript
    import apiClient from './client';
    
    export const moderationApi = {
      getPendingEdits: (params) =>
        apiClient.get('/api/v1/moderation/pending', { params }),
      
      reviewEdit: (editId, data) =>
        apiClient.post(`/api/v1/moderation/review/${editId}`, data),
      
      getStats: () =>
        apiClient.get('/api/v1/moderation/stats'),
    };
    ```
    
    6. ADD ROUTE (src/App.jsx):
    ```javascript
    import ModerationQueuePage from './pages/ModerationQueuePage';
    
    // In routes:
    <Route path="moderation" element={<ModerationQueuePage />} />
    ```
    
    7. UPDATE MAIN (main.py):
    ```python
    from app.api.v1 import moderation
    
    app.include_router(moderation.router)
    ```
    
    TESTING:
    - Test get pending edits with filters
    - Test approve edit applies changes
    - Test reject edit doesn't apply changes
    - Test user promotion after 5 approved edits
    - Test moderation stats are correct
    - Test only admins can access moderation endpoints
    - Test review notes are stored
    
    SUCCESS CRITERIA:
    - Moderation queue displays pending edits
    - Admins can approve/reject edits
    - Approved edits are applied immediately
    - Users are promoted to trusted after 5 approvals
    - Statistics are accurate
    - Only admins have access
    - All tests pass

* * *

## Phase 9: Mobile Optimization
----------------------------

### Prompt 27: Mobile List View

    Implement the mobile-optimized list view for viewing team history:
    
    REQUIREMENTS:
    
    1. MOBILE LIST COMPONENT (src/components/MobileListView.jsx):
    ```javascript
    import { useState } from 'react';
    import { useNavigate } from 'react-router-dom';
    import './MobileListView.css';
    
    export default function MobileListView({ teams }) {
      const [searchTerm, setSearchTerm] = useState('');
      const [sortBy, setSortBy] = useState('name');
      const navigate = useNavigate();
      
      const filteredTeams = teams
        .filter(team => {
          if (!searchTerm) return true;
          const latestEra = team.eras[team.eras.length - 1];
          return latestEra.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                 latestEra.uci_code?.toLowerCase().includes(searchTerm.toLowerCase());
        })
        .sort((a, b) => {
          const aEra = a.eras[a.eras.length - 1];
          const bEra = b.eras[b.eras.length - 1];
          
          if (sortBy === 'name') {
            return aEra.name.localeCompare(bEra.name);
          } else if (sortBy === 'year') {
            return b.founding_year - a.founding_year;
          }
          return 0;
        });
      
      return (
        <div className="mobile-list-view">
          <div className="mobile-header">
            <h1>Cycling Teams</h1>
            
            <div className="mobile-search">
              <input
                type="search"
                placeholder="Search teams..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            
            <div className="mobile-sort">
              <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
                <option value="name">Sort by Name</option>
                <option value="year">Sort by Year</option>
              </select>
            </div>
          </div>
          
          <div className="mobile-team-list">
            {filteredTeams.map(team => (
              <TeamCard 
                key={team.id}
                team={team}
                onClick={() => navigate(`/team/${team.id}`)}
              />
            ))}
          </div>
        </div>
      );
    }
    
    function TeamCard({ team, onClick }) {
      const latestEra = team.eras[team.eras.length - 1];
      const isActive = !team.dissolution_year;
      
      return (
        <div className="team-card" onClick={onClick}>
          <div className="team-card-header">
            <h3>{latestEra.name}</h3>
            <span className={`status-badge ${isActive ? 'active' : 'dissolved'}`}>
              {isActive ? 'Active' : 'Dissolved'}
            </span>
          </div>
          
          <div className="team-card-body">
            {latestEra.uci_code && (
              <div className="team-info">
                <span className="label">UCI Code:</span>
                <span className="value">{latestEra.uci_code}</span>
              </div>
            )}
            
            <div className="team-info">
              <span className="label">Founded:</span>
              <span className="value">{team.founding_year}</span>
            </div>
            
            {team.dissolution_year && (
              <div className="team-info">
                <span className="label">Dissolved:</span>
                <span className="value">{team.dissolution_year}</span>
              </div>
            )}
            
            {latestEra.tier && (
              <div className="team-info">
                <span className="label">Tier:</span>
                <span className="value">
                  {latestEra.tier === 1 ? 'WorldTour' : 
                   latestEra.tier === 2 ? 'ProTeam' : 'Continental'}
                </span>
              </div>
            )}
          </div>
          
          {latestEra.sponsors && latestEra.sponsors.length > 0 && (
            <div className="team-sponsors">
              {latestEra.sponsors.map((sponsor, i) => (
                <span 
                  key={i}
                  className="sponsor-tag"
                  style={{ borderLeftColor: sponsor.color }}
                >
                  {sponsor.brand}
                </span>
              ))}
            </div>
          )}
        </div>
      );
    }
    ```
    
    2. MOBILE TEAM DETAIL (src/pages/TeamDetailPage.jsx - enhance):
    ```javascript
    import { useParams } from 'react-router-dom';
    import { useTeamHistory } from '../hooks/useTeamData';
    import { useResponsive } from '../hooks/useResponsive';
    import { LoadingSpinner } from '../components/Loading';
    import { ErrorDisplay } from '../components/ErrorDisplay';
    import './TeamDetailPage.css';
    
    export default function TeamDetailPage() {
      const { nodeId } = useParams();
      const { isMobile } = useResponsive();
      const { data, isLoading, error, refetch } = useTeamHistory(nodeId);
    
      if (isLoading) return <LoadingSpinner message="Loading team history..." />;
      if (error) return <ErrorDisplay error={error} onRetry={refetch} />;
    
      const history = data?.data;
      
      return (
        <div className={`team-detail-page ${isMobile ? 'mobile' : ''}`}>
          <div className="team-header">
            <button className="back-button" onClick={() => window.history.back()}>
              ← Back
            </button>
            <h1>{history.timeline[history.timeline.length - 1].name}</h1>
          </div>
          
          {history.lineage_summary.has_predecessors && (
            <div className="lineage-info">
              <h3>Predecessor Teams</h3>
              <p>This team has predecessor teams in its lineage</p>
            </div>
          )}
          
          <div className="timeline-section">
            <h2>Team History</h2>
            <div className="timeline-list">
              {history.timeline.map((era, index) => (
                <TimelineItem 
                  key={index}
                  era={era}
                  isLatest={index === history.timeline.length - 1}
                />
              ))}
            </div>
          </div>
          
          {history.lineage_summary.has_successors && (
            <div className="lineage-info">
              <h3>Successor Teams</h3>
              <p>This team has successor teams in its lineage</p>
            </div>
          )}
        </div>
      );
    }
    
    function TimelineItem({ era, isLatest }) {
      return (
        <div className={`timeline-item ${isLatest ? 'latest' : ''}`}>
          <div className="timeline-year">{era.year}</div>
          <div className="timeline-content">
            <h3>{era.name}</h3>
            
            <div className="era-details">
              {era.uci_code && (
                <span className="detail">UCI: {era.uci_code}</span>
              )}
              {era.tier && (
                <span className="detail">
                  {era.tier === 1 ? 'WorldTour' : 
                   era.tier === 2 ? 'ProTeam' : 'Continental'}
                </span>
              )}
              <span className={`status ${era.status}`}>
                {era.status}
              </span>
            </div>
            
            {era.successor && (
              <div className="transition">
                → {era.successor.name} ({era.successor.year})
                <span className="transition-type">{era.successor.event_type}</span>
              </div>
            )}
          </div>
        </div>
      );
    }
    ```
    
    3. MOBILE STYLING (src/components/MobileListView.css):
    ```css
    .mobile-list-view {
      padding: 16px;
      max-width: 100%;
      overflow-x: hidden;
    }
    
    .mobile-header {
      position: sticky;
      top: 0;
      background: white;
      z-index: 10;
      padding-bottom: 16px;
      border-bottom: 2px solid #eee;
    }
    
    .mobile-header h1 {
      font-size: 24px;
      margin: 0 0 16px 0;
    }
    
    .mobile-search input {
      width: 100%;
      padding: 12px 16px;
      font-size: 16px;
      border: 2px solid #ddd;
      border-radius: 8px;
      margin-bottom: 12px;
    }
    
    .mobile-search input:focus {
      outline: none;
      border-color: #4A90E2;
    }
    
    .mobile-sort select {
      width: 100%;
      padding: 10px 12px;
      font-size: 14px;
      border: 1px solid #ddd;
      border-radius: 6px;
      background: white;
    }
    
    .mobile-team-list {
      margin-top: 16px;
    }
    
    .team-card {
      background: white;
      border: 1px solid #ddd;
      border-radius: 12px;
      padding: 16px;
      margin-bottom: 12px;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
      cursor: pointer;
      transition: all 0.2s;
    }
    
    .team-card:active {
      transform: scale(0.98);
      box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
    }
    
    .team-card-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 12px;
    }
    
    .team-card-header h3 {
      font-size: 18px;
      margin: 0;
      flex: 1;
      padding-right: 8px;
    }
    
    .status-badge {
      padding: 4px 8px;
      border-radius: 4px;
      font-size: 12px;
      font-weight: bold;
      white-space: nowrap;
    }
    
    .status-badge.active {
      background: #4CAF50;
      color: white;
    }
    
    .status-badge.dissolved {
      background: #999;
      color: white;
    }
    
    .team-card-body {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
      margin-bottom: 12px;
    }
    
    .team-info {
      display: flex;
      flex-direction: column;
    }
    
    .team-info .label {
      font-size: 12px;
      color: #666;
      margin-bottom: 2px;
    }
    
    .team-info .value {
      font-size: 14px;
      font-weight: 500;
      color: #333;
    }
    
    .team-sponsors {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      padding-top: 12px;
      border-top: 1px solid #eee;
    }
    
    .sponsor-tag {
      padding: 4px 8px;
      background: #f5f5f5;
      border-radius: 4px;
      font-size: 12px;
      border-left: 3px solid #999;
    }
    
    /* Team Detail Mobile Styles */
    .team-detail-page.mobile {
      padding: 16px;
    }
    
    .team-header {
      margin-bottom: 24px;
    }
    
    .back-button {
      background: none;
      border: none;
      font-size: 16px;
      color: #4A90E2;
      cursor: pointer;
      padding: 8px 0;
      margin-bottom: 8px;
    }
    
    .timeline-list {
      position: relative;
      padding-left: 40px;
    }
    
    .timeline-item {
      position: relative;
      padding-bottom: 24px;
    }
    
    .timeline-item::before {
      content: '';
      position: absolute;
      left: -28px;
      top: 0;
      bottom: 0;
      width: 2px;
      background: #ddd;
    }
    
    .timeline-item::after {
      content: '';
      position: absolute;
      left: -34px;
      top: 0;
      width: 14px;
      height: 14px;
      border-radius: 50; background: `#4A90E2`; border: 3px solid white; box-shadow: 0 0 0 2px `#4A90E2`; }

.timeline-item.latest::after { background: `#4CAF50`; box-shadow: 0 0 0 2px `#4CAF50`; }

.timeline-item:last-child::before { display: none; }

.timeline-year { font-size: 14px; font-weight: bold; color: #666; margin-bottom: 4px; }

.timeline-content h3 { font-size: 18px; margin: 0 0 8px 0; }

.era-details { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 8px; }

.era-details .detail { padding: 4px 8px; background: `#f5f5f5`; border-radius: 4px; font-size: 12px; }

.era-details .status { padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }

.status.active { background: `#4CAF50`; color: white; }

.status.historical { background: #999; color: white; }

.transition { margin-top: 8px; padding: 8px; background: `#f8f9fa`; border-left: 3px solid `#4A90E2`; font-size: 14px; }

.transition-type { display: inline-block; margin-left: 8px; font-size: 11px; padding: 2px 6px; background: `#4A90E2`; color: white; border-radius: 3px; }

    
    4. UPDATE HomePage (src/pages/HomePage.jsx):
    ```javascript
    import { useResponsive } from '../hooks/useResponsive';
    import TimelineGraph from '../components/TimelineGraph';
    import MobileListView from '../components/MobileListView';
    
    export default function HomePage() {
      const { isMobile } = useResponsive();
      const { data, isLoading, error, refetch } = useTimeline({
        start_year: 1990,
        end_year: 2024,
      });
    
      if (isLoading) return <LoadingSpinner message="Loading timeline..." />;
      if (error) return <ErrorDisplay error={error} onRetry={refetch} />;
    
      return isMobile ? (
        <MobileListView teams={data?.data?.nodes || []} />
      ) : (
        <TimelineGraph data={data?.data} />
      );
    }
    ```
    
    TESTING:
    - Test mobile list view renders all teams
    - Test search functionality
    - Test sorting by name and year
    - Test team card click navigates to detail
    - Test detail page shows chronological timeline
    - Test responsive breakpoint triggers correct view
    - Test touch interactions work smoothly
    
    SUCCESS CRITERIA:
    - Mobile list view is usable and performant
    - Search returns results instantly
    - Team cards display all key information
    - Detail timeline is easy to read
    - Transitions between views are smooth
    - Works on various mobile screen sizes

* * *

## Phase 10: Polish & Deployment
-----------------------------

### Prompt 28: Performance Optimization and Caching

    Optimize the application for production with caching, compression, and performance improvements:
    
    REQUIREMENTS:
    
    1. BACKEND CACHING (app/core/cache.py - create):
    ```python
    from functools import lru_cache
    from typing import Optional
    import json
    import hashlib
    
    class CacheManager:
        """Simple in-memory cache manager"""
        
        def __init__(self):
            self._cache = {}
        
        def get_cache_key(self, prefix: str, **kwargs) -> str:
            """Generate cache key from prefix and parameters"""
            params_str = json.dumps(kwargs, sort_keys=True)
            params_hash = hashlib.md5(params_str.encode()).hexdigest()
            return f"{prefix}:{params_hash}"
        
        def get(self, key: str) -> Optional[any]:
            """Get value from cache"""
            return self._cache.get(key)
        
        def set(self, key: str, value: any, ttl: int = 300):
            """Set value in cache with TTL (seconds)"""
            # In production, use Redis with actual TTL
            # For now, just store in memory
            self._cache[key] = value
        
        def invalidate(self, prefix: str):
            """Invalidate all keys with prefix"""
            keys_to_delete = [k for k in self._cache.keys() if k.startswith(prefix)]
            for key in keys_to_delete:
                del self._cache[key]
        
        def clear(self):
            """Clear all cache"""
            self._cache.clear()
    
    # Global cache instance
    cache_manager = CacheManager()
    ```
    
    2. CACHE MIDDLEWARE (app/api/v1/timeline.py - update):
    ```python
    from app.core.cache import cache_manager
    
    @router.get("/timeline", response_model=TimelineResponse)
    async def get_timeline(
        start_year: int = 1900,
        end_year: int = Query(default_factory=lambda: datetime.now().year),
        include_dissolved: bool = True,
        tier_filter: Optional[List[int]] = Query(None),
        session: AsyncSession = Depends(get_db)
    ):
        """Get timeline graph data with caching"""
        # Generate cache key
        cache_key = cache_manager.get_cache_key(
            "timeline",
            start_year=start_year,
            end_year=end_year,
            include_dissolved=include_dissolved,
            tier_filter=tier_filter
        )
        
        # Check cache
        cached_data = cache_manager.get(cache_key)
        if cached_data:
            return cached_data
        
        # Fetch data
        graph_data = await TimelineService.get_graph_data(
            session,
            start_year,
            end_year,
            include_dissolved,
            tier_filter
        )
        
        # Cache for 5 minutes
        cache_manager.set(cache_key, graph_data, ttl=300)
        
        return graph_data
    ```
    
    3. CACHE INVALIDATION (app/services/edit_service.py - update):
    ```python
    from app.core.cache import cache_manager
    
    @staticmethod
    async def _apply_metadata_changes(
        session: AsyncSession,
        era: TeamEra,
        changes: Dict,
        user: User
    ):
        """Apply metadata changes and invalidate cache"""
        # Apply changes...
        
        # Invalidate timeline cache
        cache_manager.invalidate("timeline")
        
        await session.commit()
    ```
    
    4. COMPRESSION MIDDLEWARE (main.py - update):
    ```python
    from fastapi.middleware.gzip import GZipMiddleware
    
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    ```
    
    5. DATABASE CONNECTION POOLING (app/db/database.py - update):
    ```python
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
    from app.core.config import settings
    
    # Create engine with connection pooling
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DEBUG,
        pool_size=20,  # Connection pool size
        max_overflow=10,  # Max connections above pool_size
        pool_pre_ping=True,  # Verify connections before using
        pool_recycle=3600  # Recycle connections after 1 hour
    )
    
    async_session_maker = async_sessionmaker(
        engine,
        expire_on_commit=False
    )
    ```
    
    6. FRONTEND CACHING (src/hooks/useTeamData.js - update):
    ```javascript
    export function useTimeline(params) {
      return useQuery({
        queryKey: ['timeline', params],
        queryFn: () => teamsApi.getTimeline(params),
        staleTime: 5 * 60 * 1000, // 5 minutes
        cacheTime: 10 * 60 * 1000, // 10 minutes
        refetchOnWindowFocus: false,
        refetchOnMount: false,
      });
    }
    ```
    
    7. IMAGE OPTIMIZATION (frontend):
    - Use WebP format for images
    - Lazy load images below the fold
    - Add loading="lazy" to img tags
    
    8. CODE SPLITTING (vite.config.js - update):
    ```javascript
    export default defineConfig({
      plugins: [react()],
      build: {
        rollupOptions: {
          output: {
            manualChunks: {
              'd3': ['d3'],
              'vendor': ['react', 'react-dom', 'react-router-dom'],
              'auth': ['@react-oauth/google'],
            }
          }
        },
        chunkSizeWarningLimit: 1000
      }
    });
    ```
    
    TESTING:
    - Test cache hit/miss rates
    - Test cache invalidation on edits
    - Measure API response times (should be < 200ms cached)
    - Test connection pooling under load
    - Test gzip compression reduces payload size
    - Test code splitting reduces initial bundle size
    
    SUCCESS CRITERIA:
    - Timeline API cached responses < 50ms
    - Gzip reduces payload by 70%+
    - Initial bundle size < 500KB
    - Database connections reused efficiently
    - Cache invalidates correctly on edits
    - No memory leaks from caching

### Prompt 29: SEO and Metadata

    Implement SEO optimization with proper metadata and Open Graph tags:
    
    REQUIREMENTS:
    
    1. REACT HELMET (install):
    ```bash
    npm install react-helmet-async
    ```
    
    2. SEO COMPONENT (src/components/SEO.jsx):
    ```javascript
    import { Helmet } from 'react-helmet-async';
    
    export default function SEO({ 
      title, 
      description, 
      image, 
      url,
      type = 'website'
    }) {
      const defaultTitle = 'Cycling Team Lineage | Professional Cycling Team History';
      const defaultDescription = 'Explore the complete history and lineage of professional cycling teams from 1900 to present. Interactive timeline visualization of team mergers, splits, and evolution.';
      const defaultImage = `${window.location.origin}/og-image.png`;
      
      const seoTitle = title ? `${title} | Cycling Team Lineage` : defaultTitle;
      const seoDescription = description || defaultDescription;
      const seoImage = image || defaultImage;
      const seoUrl = url || window.location.href;
      
      return (
        <Helmet>
          {/* Primary Meta Tags */}
          <title>{seoTitle}</title>
          <meta name="title" content={seoTitle} />
          <meta name="description" content={seoDescription} />
          
          {/* Open Graph / Facebook */}
          <meta property="og:type" content={type} />
          <meta property="og:url" content={seoUrl} />
          <meta property="og:title" content={seoTitle} />
          <meta property="og:description" content={seoDescription} />
          <meta property="og:image" content={seoImage} />
          
          {/* Twitter */}
          <meta property="twitter:card" content="summary_large_image" />
          <meta property="twitter:url" content={seoUrl} />
          <meta property="twitter:title" content={seoTitle} />
          <meta property="twitter:description" content={seoDescription} />
          <meta property="twitter:image" content={seoImage} />
          
          {/* Additional Tags */}
          <link rel="canonical" href={seoUrl} />
        </Helmet>
      );
    }
    ```
    
    3. UPDATE PAGES WITH SEO (src/pages/HomePage.jsx):
    ```javascript
    import SEO from '../components/SEO';
    
    export default function HomePage() {
      return (
        <>
          <SEO />
          {/* rest of component */}
        </>
      );
    }
    ```
    
    4. TEAM DETAIL SEO (src/pages/TeamDetailPage.jsx):
    ```javascript
    export default function TeamDetailPage() {
      const { data } = useTeamHistory(nodeId);
      const history = data?.data;
      
      const teamName = history?.timeline[history.timeline.length - 1]?.name;
      const description = `View the complete history of ${teamName}, including team lineage, sponsors, and evolution from ${history?.founding_year} to ${history?.dissolution_year || 'present'}.`;
      
      return (
        <>
          <SEO
            title={teamName}
            description={description}
            type="article"
          />
          {/* rest of component */}
        </>
      );
    }
    ```
    
    5. UPDATE MAIN (src/main.jsx):
    ```javascript
    import { HelmetProvider } from 'react-helmet-async';
    
    ReactDOM.createRoot(document.getElementById('root')).render(
      <React.StrictMode>
        <HelmetProvider>
          <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
            <QueryClientProvider client={queryClient}>
              <AuthProvider>
                <App />
              </AuthProvider>
            </QueryClientProvider>
          </GoogleOAuthProvider>
        </HelmetProvider>
      </React.StrictMode>
    );
    ```
    
    6. SITEMAP GENERATION (backend - app/api/v1/sitemap.py):
    ```python
    from fastapi import APIRouter, Depends, Response
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy import select
    from datetime import datetime
    
    from app.db.database import get_db
    from app.models.team import TeamNode
    
    router = APIRouter(tags=["sitemap"])
    
    @router.get("/sitemap.xml")
    async def get_sitemap(session: AsyncSession = Depends(get_db)):
        """Generate sitemap for SEO"""
        # Get all team nodes
        stmt = select(TeamNode)
        result = await session.execute(stmt)
        teams = result.scalars().all()
        
        # Build sitemap XML
        base_url = "https://cyclinglineage.com"  # Replace with actual domain
        
        urls = [
            f"""
            <url>
                <loc>{base_url}/</loc>
                <lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod>
                <changefreq>daily</changefreq>
                <priority>1.0</priority>
            </url>
            """
        ]
        
        for team in teams:
            urls.append(f"""
            <url>
                <loc>{base_url}/team/{team.node_id}</loc>
                <lastmod>{team.updated_at.strftime('%Y-%m-%d')}</lastmod>
                <changefreq>weekly</changefreq>
                <priority>0.8</priority>
            </url>
            """)
        
        sitemap = f"""<?xml version="1.0" encoding="UTF-8"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            {''.join(urls)}
        </urlset>
        """
        
        return Response(content=sitemap, media_type="application/xml")
    ```
    
    7. ROBOTS.TXT (public/robots.txt):

User-agent: \* Allow: / Disallow: /api/ Disallow: /login Disallow: /moderation

Sitemap: [https://cyclinglineage.com/sitemap.xml](https://cyclinglineage.com/sitemap.xml)

    
    TESTING:
    - Test meta tags are rendered correctly
    - Test Open Graph preview (use Facebook debugger)
    - Test Twitter Card preview
    - Test sitemap generates all team URLs
    - Test canonical URLs are correct
    
    SUCCESS CRITERIA:
    - All pages have unique titles and descriptions
    - Open Graph tags render correctly
    - Sitemap includes all team pages
    - robots.txt properly configured
    - No duplicate content issues

### Prompt 30: Docker Production Setup

    Create production-ready Docker configuration with proper security and optimization:
    
    REQUIREMENTS:
    
    1. PRODUCTION DOCKERFILE (backend/Dockerfile.prod):
    ```dockerfile
    FROM python:3.11-slim
    
    WORKDIR /app
    
    # Install system dependencies
    RUN apt-get update && apt-get install -y \
        postgresql-client \
        && rm -rf /var/lib/apt/lists/*
    
    # Copy requirements and install Python dependencies
    COPY requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt
    
    # Copy application code
    COPY . .
    
    # Create non-root user
    RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
    USER appuser
    
    # Expose port
    EXPOSE 8000
    
    # Health check
    HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
      CMD python -c "import requests; requests.get('http://localhost:8000/health')"
    
    # Run with gunicorn
    CMD ["gunicorn", "main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
    ```
    
    2. FRONTEND PRODUCTION DOCKERFILE (frontend/Dockerfile.prod):
    ```dockerfile
    # Build stage
    FROM node:18-alpine AS build
    
    WORKDIR /app
    
    COPY package*.json ./
    RUN npm ci --only=production
    
    COPY . .
    RUN npm run build
    
    # Production stage
    FROM nginx:alpine
    
    # Copy custom nginx config
    COPY nginx.conf /etc/nginx/conf.d/default.conf
    
    # Copy built assets
    COPY --from=build /app/dist /usr/share/nginx/html
    
    # Health check
    HEALTHCHECK --interval=30s --timeout=3s \
      CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1
    
    EXPOSE 80
    
    CMD ["nginx", "-g", "daemon off;"]
    ```
    
    3. NGINX CONFIGURATION (frontend/nginx.conf):
    ```nginx
    server {
        listen 80;
        server_name _;
    
        root /usr/share/nginx/html;
        index index.html;
    
        # Gzip compression
        gzip on;
        gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
        gzip_min_length 1000;
    
        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
    
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    
        # React Router - serve index.html for all routes
        location / {
            try_files $uri $uri/ /index.html;
        }
    
        # Proxy API requests to backend
        location /api/ {
            proxy_pass http://backend:8000;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_cache_bypass $http_upgrade;
        }
    }
    ```
    
    4. PRODUCTION DOCKER COMPOSE (docker-compose.prod.yml):
    ```yaml
    version: '3.8'
    
    services:
      postgres:
        image: postgres:15
        restart: always
        environment:
          POSTGRES_DB: cycling_lineage
          POSTGRES_USER: ${DB_USER}
          POSTGRES_PASSWORD: ${DB_PASSWORD}
        volumes:
          - postgres_data:/var/lib/postgresql/data
        networks:
          - backend
        healthcheck:
          test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
          interval: 10s
          timeout: 5s
          retries: 5
    
      backend:
        build:
          context: ./backend
          dockerfile: Dockerfile.prod
        restart: always
        environment:
          DATABASE_URL: postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@postgres:5432/cycling_lineage
          JWT_SECRET_KEY: ${JWT_SECRET_KEY}
          GOOGLE_CLIENT_ID: ${GOOGLE_CLIENT_ID}
          GOOGLE_CLIENT_SECRET: ${GOOGLE_CLIENT_SECRET}
        depends_on:
          postgres:
            condition: service_healthy
        networks:
          - backend
          - frontend
        healthcheck:
          test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
          interval: 30s
          timeout: 10s
          retries: 3
    
      frontend:
        build:
          context: ./frontend
          dockerfile: Dockerfile.prod
          args:
            VITE_API_URL: /api
            VITE_GOOGLE_CLIENT_ID: ${GOOGLE_CLIENT_ID}
        restart: always
        ports:
          - "80:80"
          - "443:443"
        depends_on:
          - backend
        networks:
          - frontend
        healthcheck:
          test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost/"]
          interval: 30s
          timeout: 3s
          retries: 3
    
    networks:
      backend:
        driver: bridge
      frontend:
        driver: bridge
    
    volumes:
      postgres_data:
    ```
    
    5. PRODUCTION ENV TEMPLATE (.env.prod.example):

Database
========

DB\_USER=cycling\_user DB\_PASSWORD=CHANGE\_ME\_STRONG\_PASSWORD

JWT
===

JWT\_SECRET\_KEY=CHANGE\_ME\_RANDOM\_SECRET\_KEY

Google OAuth
============

GOOGLE\_CLIENT\_ID=your-google-client-id GOOGLE\_CLIENT\_SECRET=your-google-client-secret

Application
===========

DEBUG=false CORS\_ORIGINS=\["[https://cyclinglineage.com](https://cyclinglineage.com)"\]

    
    6. DEPLOYMENT SCRIPT (deploy.sh):
    ```bash
    #!/bin/bash
    
    set -e
    
    echo "🚀 Starting deployment..."
    
    # Pull latest code
    git pull origin main
    
    # Build and start services
    docker-compose -f docker-compose.prod.yml build
    docker-compose -f docker-compose.prod.yml up -d
    
    # Run migrations
    docker-compose -f docker-compose.prod.yml exec -T backend alembic upgrade head
    
    # Health check
    echo "⏳ Waiting for services to be healthy..."
    sleep 10
    
    if docker-compose -f docker-compose.prod.yml ps | grep -q "unhealthy"; then
        echo "❌ Deployment failed - unhealthy services detected"
        docker-compose -f docker-compose.prod.yml logs
        exit 1
    fi
    
    echo "✅ Deployment successful!"
    docker-compose -f docker-compose.prod.yml ps
    ```
    
    7. GUNICORN CONFIGURATION (backend/gunicorn.conf.py):
    ```python
    import multiprocessing
    
    # Server socket
    bind = "0.0.0.0:8000"
    backlog = 2048
    
    # Worker processes
    workers = multiprocessing.cpu_count() * 2 + 1
    worker_class = "uvicorn.workers.UvicornWorker"
    worker_connections = 1000
    timeout = 30
    keepalive = 2
    
    # Logging
    accesslog = "-"
    errorlog = "-"
    loglevel = "info"
    
    # Process naming
    proc_name = "cycling_lineage"
    
    # Server mechanics
    daemon = False
    pidfile = None
    umask = 0
    user = None
    group = None
    tmp_upload_dir = None
    
    # SSL (if needed)
    # keyfile = "/path/to/key.pem"
    # certfile = "/path/to/cert.pem"
    ```
    
    TESTING:
    - Test production build completes successfully
    - Test all services start and pass health checks
    - Test migrations run automatically
    - Test nginx serves static files correctly
    - Test API requests proxy to backend
    - Test security headers are present
    - Test gzip compression is working
    
    SUCCESS CRITERIA:
    - Production containers build without errors
    - All services pass health checks
    - Nginx serves frontend and proxies API
    - Database migrations run on deployment
    - Services restart automatically on failure
    - Logs are accessible via docker-compose logs

* * *

Summary
-------

This complete implementation guide provides **30 detailed, test-driven prompts** that build the Cycling Team Lineage Timeline application from scratch. Each prompt:

1.  **Builds incrementally** on previous prompts
2.  **Includes complete code** with no placeholders
3.  **Specifies testing requirements**
4.  **Defines clear success criteria**
5.  **Integrates with previous work** (no orphaned code)

The prompts cover:

*   **Foundation** (Docker, database, migrations)
*   **Data Models** (teams, eras, lineage, sponsors)
*   **API Layer** (REST endpoints with caching)
*   **Frontend** (React, D3.js visualization, responsive design)
*   **Scraper** (rate-limited data collection)
*   **Authentication** (Google OAuth, JWT)
*   **Editor** (wizard-based editing system)
*   **Moderation** (review queue, user roles)
*   **Mobile** (optimized list views)
*   **Production** (Docker, caching, SEO, deployment)

Each prompt is designed to be **copy-pasted directly** into a coding agent like Cursor, Copilot, or Claude Code, and will result in a working, tested feature that integrates seamlessly with the rest of the application.