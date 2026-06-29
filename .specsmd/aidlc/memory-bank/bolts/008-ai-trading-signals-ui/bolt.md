---
id: 008-ai-trading-signals-ui
unit: 004-ai-trading-signals-ui
intent: 001-ai-trading-signals
type: simple-construction-bolt
status: planned
stories:
  - 003-instrument-filtering-search
  - 004-performance-charts
created: 2026-06-18T01:38:00Z
started: null
completed: null
current_stage: null
stages_completed: []

requires_bolts:
  - 007-ai-trading-signals-ui
  - 005-backtesting
enables_bolts:
  - 009-ai-trading-signals-ui
requires_units: []
blocks: true

complexity:
  avg_complexity: 2
  avg_uncertainty: 1
  max_dependencies: 2
  testing_scope: 2
---

# Bolt: 008-ai-trading-signals-ui

## Overview
Second UI bolt: implement instrument filtering/search and performance/backtest visualization charts.

## Objective
Add instrument filtering, confidence threshold controls, and interactive performance charts from backtest data.

## Stories Included

- **003-instrument-filtering-search**: Instrument filtering and search (Must)
- **004-performance-charts**: Performance charts and backtest visualization (Should)

## Bolt Type

**Type**: Simple Construction Bolt
**Definition**: `.specsmd/aidlc/templates/construction/bolt-types/simple-construction-bolt.md`

## Stages

- [ ] **1. design**: Pending → component design
- [ ] **2. implement**: Pending → code
- [ ] **3. test**: Pending → test report

## Dependencies

### Requires
- 007-ai-trading-signals-ui (Signal feed must exist)
- 005-backtesting (Backtest metrics API)

### Enables
- 009-ai-trading-signals-ui (Notifications)

## Success Criteria

- [ ] Filters update signal feed in real-time
- [ ] Performance charts render from backtest data
- [ ] Interactive charts with zoom and hover tooltips
- [ ] All stories acceptance criteria met
- [ ] Tests passing
