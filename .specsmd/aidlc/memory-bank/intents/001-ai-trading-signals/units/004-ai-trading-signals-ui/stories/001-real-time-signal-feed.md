---
id: 001-real-time-signal-feed
unit: 004-ai-trading-signals-ui
intent: 001-ai-trading-signals
status: draft
priority: must
created: 2026-06-18T01:37:00Z
assigned_bolt: null
implemented: false
---

# Story: 001-real-time-signal-feed

## User Story

**As a** trader
**I want** a real-time scrolling feed of trading signals
**So that** I can see new signals as they are generated

## Acceptance Criteria

- [ ] **Given** a new signal is generated, **When** the dashboard is open, **Then** the signal appears in the feed within 500ms without page refresh
- [ ] **Given** the signal feed, **When** displayed, **Then** each signal shows instrument, type (buy/sell/hold), confidence score, and timestamp
- [ ] **Given** high-confidence signals, **When** confidence exceeds the configured threshold, **Then** the signal is visually highlighted (green for buy, red for sell)
- [ ] **Given** a large number of signals, **When** the feed grows, **Then** old signals are paginated and virtualized for performance

## Technical Notes

- Next.js frontend with Supabase Realtime subscription
- Virtual scrolling for performance with large datasets
- Color-coded signal types with confidence badges
- Refresh interval configurable (default: real-time)

## Dependencies

### Requires
- Backend: 002-signal-engine API

### Enables
- 002-signal-detail-view

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| WebSocket disconnects | Auto-reconnect, show "reconnecting" indicator |
| 100 signals arrive in 1 second | Batch update DOM, not per-signal |
| Empty feed (no signals yet) | Show empty state with helpful message |
