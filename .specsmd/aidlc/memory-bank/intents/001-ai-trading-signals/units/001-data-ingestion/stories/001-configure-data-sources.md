---
id: 001-configure-data-sources
unit: 001-data-ingestion
intent: 001-ai-trading-signals
status: draft
priority: must
created: 2026-06-18T01:36:00Z
assigned_bolt: null
implemented: false
---

# Story: 001-configure-data-sources

## User Story

**As a** system admin
**I want** to configure market data sources via a pluggable adapter system
**So that** I can add, enable, or disable different data providers

## Acceptance Criteria

- [ ] **Given** a new data provider API, **When** I create a new adapter class implementing the provider interface, **Then** the system discovers and registers it automatically
- [ ] **Given** I have configured provider credentials, **When** the system starts, **Then** it connects and authenticates with the provider
- [ ] **Given** a provider is rate-limited, **When** requests exceed the limit, **Then** requests are queued and retried with backoff
- [ ] **Given** a provider fails to respond, **When** data is requested, **Then** the system falls back to cached data and logs the error

## Technical Notes

- Use strategy/adapter pattern for provider abstraction
- Store provider config in Supabase PostgreSQL (DataSource entity)
- Implement Redis-based rate limiting per provider
- Async HTTP with httpx for provider requests

## Dependencies

### Requires
- None

### Enables
- 002-data-fetching-normalization

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| API key expires mid-operation | Log error, flag provider as invalid |
| Multiple providers for same instrument | Return consolidated data with source metadata |
| Provider returns malformed data | Log warning, skip that data point |
