---
id: 002-signal-detail-view
unit: 004-ai-trading-signals-ui
intent: 001-ai-trading-signals
status: draft
priority: must
created: 2026-06-18T01:37:00Z
assigned_bolt: null
implemented: false
---

# Story: 002-signal-detail-view

## User Story

**As a** trader
**I want** to click a signal to see full details and rationale
**So that** I can make informed trading decisions

## Acceptance Criteria

- [ ] **Given** a signal in the feed, **When** clicked, **Then** a detail panel opens showing full signal metadata (confidence, model version, timestamp, supporting features)
- [ ] **Given** the detail view, **When** displayed, **Then** it shows the model's rationale and top contributing features
- [ ] **Given** the detail view, **When** available, **Then** it shows recent price chart with signal marker
- [ ] **Given** the detail view is open, **When** a new signal arrives for the same instrument, **Then** the detail view updates in real-time

## Technical Notes

- Slide-over panel or modal component
- Embed small price chart using Recharts
- Show feature importance visualization
- Responsive: full-screen on mobile, side panel on desktop

## Dependencies

### Requires
- 001-real-time-signal-feed

### Enables
- Informed decision making

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Signal deleted (backfill correction) | Show "signal no longer available" |
| Very long rationale text | Collapsible with "show more" |
| No chart data available | Show text-only view with note |
