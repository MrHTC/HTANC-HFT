---
id: 003-instrument-filtering-search
unit: 004-ai-trading-signals-ui
intent: 001-ai-trading-signals
status: draft
priority: must
created: 2026-06-18T01:37:00Z
assigned_bolt: null
implemented: false
---

# Story: 003-instrument-filtering-search

## User Story

**As a** trader
**I want** to filter signals by instrument, type, and minimum confidence
**So that** I can focus on signals relevant to my strategy

## Acceptance Criteria

- [ ] **Given** the signal feed, **When** I select an instrument from the filter, **Then** only signals for that instrument are shown
- [ ] **Given** filters are applied, **When** I adjust the confidence slider, **Then** signals below the threshold are hidden
- [ ] **Given** the filter panel, **When** I select multiple instruments, **Then** signals for all selected instruments are shown
- [ ] **Given** filters are active, **When** a new signal arrives, **Then** it respects the active filters before appearing
- [ ] **Given** filter state, **When** I switch between markets (stocks/crypto/forex), **Then** only instruments from that market are available in the selector

## Technical Notes

- URL-based filter state for shareable links
- Debounced search for instrument lookup
- Confidence slider with visual feedback
- Save filter presets in local storage

## Dependencies

### Requires
- 001-real-time-signal-feed

### Enables
- Focused signal analysis

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Filter matches zero signals | Show "no signals match filters" with clear filter button |
| Very many instruments (500+) | Virtualized dropdown with search |
| Filters too restrictive | Counter showing how many signals are hidden |
