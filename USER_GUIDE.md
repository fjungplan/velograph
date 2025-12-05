# ChainLines – User Guide
### The ChainLines Timeline

## Overview
ChainLines visualizes and manages the historical evolution of professional cycling teams, including mergers, splits, and successions, using a structured data model and interactive UI.

## Key Concepts
- **Team Node**: Represents a legal/managerial entity (the core of a team across years).
- **Team Era**: A single season snapshot of a team (name, sponsors, tier, etc.).
- **Lineage Event**: Records structural changes (succession, merge, split) between teams.

## Public Read API (Phase 2 – Prompt 7)
These endpoints provide read-only access to team nodes and eras.

- GET `/api/v1/teams`
  - Query: `skip` (default 0), `limit` (default 50, max 100), `active_in_year` (optional), `tier_level` (optional)
  - Returns: `{ items: TeamNodeResponse[], total, skip, limit }`

- GET `/api/v1/teams/{node_id}`
  - Returns a single `TeamNode` with its eras and lineage relationships
  - 404 if the node does not exist

- GET `/api/v1/teams/{node_id}/eras`
  - Query: `year` (optional)
  - Returns all eras for a node, ordered by `season_year` DESC

Notes
- Path parameter `node_id` must be a valid UUID; invalid input returns a 422 validation error.
- OpenAPI docs at `/docs` detail schemas and allow trying requests in the browser.

## Canonicalization of MERGE/SPLIT Events
### What Changed?
To ensure data integrity and clarity, the system now automatically converts ("canonicalizes") any attempted MERGE or SPLIT event that only has a single leg (i.e., only one predecessor or one successor) into a standard succession event (LEGAL_TRANSFER or SPIRITUAL_SUCCESSION). This prevents accidental mislabeling and keeps the lineage graph semantically correct.

- **MERGE**: Only used when two or more teams combine into one (multiple predecessors, one successor, same year).
- **SPLIT**: Only used when one team branches into two or more (one predecessor, multiple successors, same year).
- **Succession**: Any one-to-one transition (one predecessor, one successor) is always a LEGAL_TRANSFER or SPIRITUAL_SUCCESSION, never a MERGE or SPLIT.

### Why?
- Prevents confusion in the graph and analytics.
- Ensures that warnings about incomplete merges/splits do not persist indefinitely.
- Keeps the data model clean and easy to interpret.

### How It Works
- When a MERGE or SPLIT is created, the system checks if there are at least two related events for the same node and year.
- If not, the event is automatically reclassified as a succession (LEGAL_TRANSFER by default; can be changed to SPIRITUAL_SUCCESSION if needed).
- Any warning notes about incomplete merges/splits are removed.

## Documentation Structure
- This `USER_GUIDE.md` provides a high-level overview and key user-facing logic.
- As the project grows, consider splitting documentation:
  - `docs/BACKEND.md`: API, data model, migrations, backend setup.
  - `docs/FRONTEND.md`: UI, visualization, React usage, D3.js.
  - `docs/DATA_MANAGEMENT.md`: Admin tools, data import/export, moderation.
  - `docs/CONTRIBUTING.md`: For developers and contributors.

## Further Reading
- See the in-app help or the `/docs` folder for more details on specific features.
- For technical details, refer to the backend and frontend documentation as they are developed.

## Timeline Endpoint and Caching
The timeline graph endpoint provides D3-friendly data:

- GET `/api/v1/timeline`
  - Query params: `start_year`, `end_year`, `include_dissolved`, `tier_filter`
  - Response: `{ nodes: [...], links: [...], meta: { year_range, node_count, link_count } }`

### Performance and Caching
- The timeline endpoint uses an optional in-memory cache to speed up repeated requests.
- Configure in `app/core/config.py`:
  - `TIMELINE_CACHE_ENABLED`: enable/disable caching (default: true)
  - `TIMELINE_CACHE_TTL_SECONDS`: cache TTL in seconds (default: 300)
- Cache invalidation is automatic when timeline-affecting data changes:
  - Creating eras
  - Linking sponsors to eras
  - Creating lineage events
- Manual invalidation (ops/debugging):
  - `POST /api/v1/admin/cache/invalidate`
  - PowerShell example:
    ```powershell
    Invoke-RestMethod -Uri "http://localhost:8000/api/v1/admin/cache/invalidate" -Method Post
    ```
  - Note: Protect admin endpoints in production with proper authentication/authorization.
 
### Client Caching Headers & Conditional Requests
To improve performance, read endpoints return `Cache-Control` and `ETag` headers and support conditional requests:

- Cache-Control: `max-age=300` on timeline and teams read endpoints.
- ETag: Weak ETag (`W/"..."`) computed from the canonical JSON of the response.
- Conditional 304: Clients may send `If-None-Match`; if the tag matches, the server returns `304 Not Modified`.

Affected endpoints:
- `GET /api/v1/timeline`
- `GET /api/v1/teams/{node_id}`
- `GET /api/v1/teams/{node_id}/eras`
- `GET /api/v1/teams`

PowerShell example:
```powershell
# First request
$resp = Invoke-WebRequest -Uri http://localhost:8000/api/v1/timeline
$etag = $resp.Headers["ETag"]

# Conditional request
Invoke-WebRequest -Uri http://localhost:8000/api/v1/timeline -Headers @{"If-None-Match"=$etag}
```

### Testing & CI on Windows
For stable test runs on Windows, enable Python faulthandler:

- Local: `python -X faulthandler -m pytest -q`
- CI: GitHub Actions workflow uses `windows-latest` with faulthandler enabled for backend tests.
