---
id: 003-signal-generation-api
unit: 002-signal-engine
intent: 001-ai-trading-signals
status: draft
priority: must
created: 2026-06-18T01:37:00Z
assigned_bolt: null
implemented: false
---

# Story: 003-signal-generation-api

## User Story

**As a** trader or dashboard
**I want** a REST API to query generated signals
**So that** I can view current and historical trading signals

## Acceptance Criteria

- [ ] **Given** model inference completes, **When** a signal is generated, **Then** it is stored with id, instrument, timestamp, type (buy/sell/hold), confidence score, and rationale
- [ ] **Given** a GET /api/v1/signals request, **When** valid filters are provided, **Then** returns filtered, paginated signals
- [ ] **Given** a request for latest signals, **When** no filters specified, **Then** returns top N most recent high-confidence signals
- [ ] **Given** signal metadata, **When** queried by id, **Then** returns full signal detail including supporting features and model version

## Technical Notes

- FastAPI route with filtering (instrument, min_confidence, type, date_range)
- Store signals in Supabase PostgreSQL
- Implement redis caching for frequently queried signals
- Include pagination metadata in response

## Dependencies

### Requires
- 002-model-loading-inference

### Enables
- Dashboard display of signals

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| No signals generated yet | Return empty array with 200 |
| Filter with no matches | Return empty array, not error |
| Very high query frequency | Cache popular queries, rate limit API |
