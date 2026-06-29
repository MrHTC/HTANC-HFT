---
id: 002-data-fetching-normalization
unit: 001-data-ingestion
intent: 001-ai-trading-signals
status: draft
priority: must
created: 2026-06-18T01:36:00Z
assigned_bolt: null
implemented: false
---

# Story: 002-data-fetching-normalization

## User Story

**As a** signal engine
**I want** normalized market data from all providers in a unified format
**So that** I can compute features without provider-specific handling

## Acceptance Criteria

- [ ] **Given** raw data from any provider, **When** it passes through the normalization pipeline, **Then** it conforms to the unified schema (open, high, low, close, volume, timestamp)
- [ ] **Given** scheduled data fetch triggers, **When** the cron fires, **Then** data is fetched from all enabled providers for configured instruments
- [ ] **Given** a data fetch completes, **When** data is normalized, **Then** it is stored in Supabase PostgreSQL with source metadata
- [ ] **Given** duplicate data from overlapping providers, **When** normalized, **Then** duplicates are deduplicated by timestamp+instrument

## Technical Notes

- Use Pydantic models for schema validation
- Implement UPSERT logic for deduplication
- Support configurable fetch intervals per provider
- Store raw and normalized data for audit trail

## Dependencies

### Requires
- 001-configure-data-sources

### Enables
- 003-market-data-query-api
- 004-realtime-streaming

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Weekend/no trading hours | Return empty, no error |
| Split/dividend adjustment | Flag with adjustment metadata |
| Very high volume data (1-min bars) | Batch insert, throttle to avoid DB overload |
