# Phase C: Endpoint Headers & Consistency

## Goals
- Apply `Cache-Control` and weak `ETag` across all read endpoints consistently
- Ensure conditional `304 Not Modified` behavior via `If-None-Match`
- Tighten DTO/Response casing (snake_case) and meta fields alignment
- Extend tests covering headers and conditional requests

## Scope
- Teams: list, detail, eras (already updated; verify)
- Timeline: graph endpoint (already updated; verify)
- Health: no caching; validate consistent JSON shape
- Admin: no caching; unchanged

## Testing
- Add targeted tests for `ETag` presence and `304` responses
- Verify existing guard tests still pass and no async lazy-load regressions

## CI
- Ensure Windows workflow runs tests with faulthandler and remains green
