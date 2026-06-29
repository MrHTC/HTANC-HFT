---
id: 004-performance-charts
unit: 004-ai-trading-signals-ui
intent: 001-ai-trading-signals
status: draft
priority: should
created: 2026-06-18T01:37:00Z
assigned_bolt: null
implemented: false
---

# Story: 004-performance-charts

## User Story

**As a** trader
**I want** to see performance charts and backtest results
**So that** I can assess the historical accuracy of signals

## Acceptance Criteria

- [ ] **Given** backtest data is available, **When** the performance tab is selected, **Then** shows accuracy trend chart over time
- [ ] **Given** performance view, **When** displayed, **Then** shows key metrics cards: overall accuracy, signals count, win rate
- [ ] **Given** backtest results, **When** viewed per-instrument, **Then** shows instrument-specific accuracy and performance
- [ ] **Given** model comparison data, **When** available, **Then** shows side-by-side comparison chart
- [ ] **Given** the charts, **When** rendered, **Then** they are interactive (zoom, hover tooltips)

## Technical Notes

- Use Recharts for React chart components
- Time-series charts with date range selector
- Metrics cards with sparkline trends
- Export chart data as CSV button

## Dependencies

### Requires
- Backend: 003-backtesting API

### Enables
- Performance-driven model selection

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| No backtest data yet | Show placeholder with "run first backtest" action |
| Single data point | Show as dot, not line |
| Very long time range | Downsample data points for rendering |
