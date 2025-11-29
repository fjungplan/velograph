# Velograph Refactor Plan

## Objectives
- Stabilize async behavior and eliminate lazy-load triggers in the read API.
- Standardize service/repository boundaries and error semantics.
- Improve performance with predictable eager-loading + caching.
- Prepare the backend for Prompt 10 frontend integration.

## Principles
- Non-functional refactor first: retain API contracts unless clearly beneficial.
- Small, reviewable PRs with targeted tests per change.
- Prefer `selectinload` and explicit projections over ad-hoc relationship access.
- Keep Pydantic v2 models lean; minimize nested payloads for mobile.

## Phase A — Data Access Hygiene
- Audit repositories (`TeamRepository`, timeline-related):
	- Ensure all read paths load relationships via `selectinload`.
	- Add explicit `.options(...)` in repository methods rather than services.
- Extract light DTO builders for common views (timeline era, team summary).
- Add guardrails: no lazy-loads in async during serialization.

### Status (2025-11-28): Completed
- Implementation:
	- Centralized eager-loading in `backend/app/repositories/team_repository.py` and `backend/app/services/lineage_service.py`.
	- Ensured `timeline_service` preloads `TeamEra.sponsor_links.brand` and lineage event nodes.
	- Added DTOs in `backend/app/services/dto.py` and refactored `backend/app/core/graph_builder.py` to consume them.
	- Expanded guards in `backend/tests/api/test_no_lazy_load.py` to cover history, timeline, eras, team list/detail, sponsor service composition, and timeline sponsor shape.
- Validation:
	- Test suite result: 82 passed, 1 skipped in ~10s.
	- Targeted guard tests consistently pass; no async lazy-load regressions observed.
- Notes:
	- Health test stabilized by mocking DB connectivity in success case to avoid coupling to external Postgres during tests.
	- No breaking changes to API contracts; timeline payloads slightly leaner via DTOs.

## Phase B — Service Layer Consolidation
 - Clarify responsibilities:
	- `TeamService`: write operations, validations.
	- `TeamDetailService`: team history assembly + transition classification.
	- `TimelineService`: graph building and range filters.
- Extract shared utilities:
	- Status calculation (active/historical/dissolved).
	- Transition classification (MERGED_INTO, ACQUISITION, REVIVAL, SPLIT).
- Define `ServiceError` types → consistent HTTP mapping in routers.

### Status (2025-11-29): Completed
- Timeline:
	- Repository refactored to mapped `selectinload`; lambda loaders removed.
	- Service ensures eras are initialized to avoid async lazy-load; caching retained.
	- GraphBuilder emits snake_case fields; Pydantic v2 alignment verified.
	- Targeted timeline + guard tests pass.

- Teams:
	- `TeamRepository` provides `get_by_id`, `get_all`, `get_eras_for_node` with eager-loads.
	- `TeamService` now delegates for `get_node_with_eras`, `list_nodes`, `get_node_eras`, adding defensive `eras` initialization.
	- `api/v1/teams.py` wired to `TeamService` for get/list/eras.
	- Tests: teams API (4) and guard (7) pass; team service integration (2) pass.

- Health/CI:
	- Health endpoint stabilized via DI checker; tests deterministic.
	- Added GitHub Actions workflow to run backend tests on Windows with `python -X faulthandler -m pytest -q`.
	- Makefile `test` target updated to use faulthandler in container.

- ETag/Cache:
	- Added `backend/app/core/etag.py` for weak ETag computation from canonical JSON.
	- Timeline and teams endpoints return `Cache-Control: max-age=300` and `ETag` headers.
	- Conditional `304 Not Modified` responses via `If-None-Match` header support.
	- Tests verify ETag presence, 304 behavior, and changes on data mutation/pagination.

## Phase C — API Consistency & Caching
- Standardize headers on mobile endpoints:
	- `Cache-Control: max-age=300`
	- `ETag` + `If-None-Match` → 304 when unchanged.
- Normalize query/path validation with FastAPI `Query(..., ge/le)` and UUID parsing.
- Ensure consistent 400/404/5xx semantics across endpoints.

### Status (2025-11-29): Completed
- Extended test coverage:
	- `backend/tests/api/test_headers_etag_changes.py`: ETag changes on data mutation and pagination.
	- `backend/tests/api/test_timeline_meta_consistency.py`: Meta field validation (snake_case, counts).
- Verified ETag/Cache-Control behavior across timeline and teams endpoints.
- Full suite: 90 passed, 1 skipped with faulthandler.

## Phase D — Tests & CI
- Unit tests: assert no async lazy loads (history, timeline, sponsors).
- Integration tests: SQLite fixtures; Postgres CI via Alembic migrations.
- Light perf checks: response size bounds, query count where practical.
- Keep CI single-run; avoid duplicate triggers.

### Status (2025-11-29): Completed
- Graph invariants:
	- `backend/tests/api/test_graph_invariants.py`: Verifies deterministic ordering, unique node IDs, no orphan links, filter subset behavior.
- GraphBuilder improvements:
	- Deterministic ordering: nodes by founding_year→id; eras by year→name; links by year→source→target→type.
	- Snake_case fields aligned; comments added for clarity.
- Full suite: 93 passed, 1 skipped with faulthandler.

## Phase E — Documentation & DevEx
- Update `USER_GUIDE.md` with ETag/Cache-Control behavior and conditional requests.
- Add README notes on async pitfalls and eager-loading strategy.
- Track milestones in `prompts/todo.md` for visibility.

### Status (2025-11-29): Completed
- `USER_GUIDE.md` updated with:
	- Client caching headers and conditional request examples.
	- Windows testing guidance with faulthandler.
- `README.md` updated with:
	- Async pitfalls and eager-loading best practices.
	- ETag/Cache-Control documentation.
	- Windows CI notes on expected access violations.

## Milestones
- [x] Repositories use `selectinload` consistently with explicit options.
- [x] Services share utilities and avoid implicit lazy loads.
- [x] Endpoints standardized: headers + error mapping.
- [x] Tests pass locally and CI; perf checks added.
- [x] Docs updated; frontend Prompt 10 ready.

## Completion Summary (2025-11-29)
All refactoring phases (A-E) completed and merged to main via PRs #3, #4, #5.
- Full test suite: 93 passed, 1 skipped
- No breaking API changes
- Performance improved via caching and eager-loading
- Documentation updated for developers and users

## Risks & Mitigations
- Hidden lazy-load regressions → add tests that serialize responses under async and fail on lazy access.
- Scope creep → keep PRs small, phase-by-phase, link back to this plan.

## Delivery Plan
- Open incremental PRs from `refactor/intermediate-phase` to `main` per phase.
- Each PR includes: brief description, tests touched, and any perf observations.
