---
id: 004-realtime-streaming
unit: 001-data-ingestion
intent: 001-ai-trading-signals
status: draft
priority: should
created: 2026-06-18T01:36:00Z
assigned_bolt: null
implemented: false
---

# Story: 004-realtime-streaming

## User Story

**As a** trader
**I want** real-time market data streaming via WebSocket
**So that** I can see price movements as they happen

## Acceptance Criteria

- [ ] **Given** a WebSocket connection is established, **When** a new market data point arrives, **Then** it is pushed to all subscribed clients within 100ms
- [ ] **Given** a client subscribes to specific instruments, **When** data arrives for other instruments, **Then** it is not sent to that client
- [ ] **Given** a client disconnects, **When** they reconnect, **Then** they receive the latest N data points for their subscribed instruments
- [ ] **Given** high-frequency updates, **When** multiple updates arrive rapidly, **Then** they are batched at 100ms intervals

## Technical Notes

- Use Supabase Realtime for WebSocket infrastructure
- Alternatively, implement FastAPI WebSocket endpoints
- Implement client-side throttling configurable per connection

## Dependencies

### Requires
- 002-data-fetching-normalization

### Enables
- Real-time dashboard updates

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Too many concurrent connections | Enforce max connections per IP, queue |
| Slow consumer falls behind | Drop old messages, send latest snapshot |
| Network partition | Client reconnects with auto-retry |
