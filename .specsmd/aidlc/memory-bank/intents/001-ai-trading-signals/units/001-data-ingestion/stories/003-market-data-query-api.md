---
id: 003-market-data-query-api
unit: 001-data-ingestion
intent: 001-ai-trading-signals
status: draft
priority: must
created: 2026-06-18T01:36:00Z
assigned_bolt: null
implemented: false
---

# Story: 003-market-data-query-api

## User Story

**As a** signal engine or dashboard
**I want** a REST API to query market data by instrument, date range, and interval
**So that** I can retrieve historical and real-time data on demand

## Acceptance Criteria

- [ ] **Given** valid query parameters, **When** GET /api/v1/market-data is called, **Then** returns paginated results filtered by instrument, date range, and interval
- [ ] **Given** a request for latest data, **When** no date range is specified, **Then** returns the most recent N data points
- [ ] **Given** an invalid instrument ID, **When** queried, **Then** returns 404 with error message
- [ ] **Given** a request for aggregated data (e.g., daily OHLCV from 1-min bars), **When** interval parameter is provided, **Then** returns correctly aggregated data

## Technical Notes

- FastAPI route with Pydantic query params
- Support intervals: 1m, 5m, 15m, 1h, 1d
- Implement cursor-based pagination for large result sets
- Cache frequent queries in Redis with TTL

## Dependencies

### Requires
- 002-data-fetching-normalization

### Enables
- Signal engine feature computation
- Dashboard data display

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Date range with no data | Return empty results array |
| Very large date range | Paginate, return first page with total count |
| Intraday after market close | Return last cached data |
