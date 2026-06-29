---
id: 002-performance-metrics-reporting
unit: 003-backtesting
intent: 001-ai-trading-signals
status: draft
priority: must
created: 2026-06-18T01:37:00Z
assigned_bolt: null
implemented: false
---

# Story: 002-performance-metrics-reporting

## User Story

**As a** admin
**I want** detailed performance reports from backtest runs
**So that** I can assess signal accuracy and model effectiveness

## Acceptance Criteria

- [ ] **Given** a completed backtest run, **When** results are computed, **Then** accuracy, precision, recall, F1-score, and simulated P&L are calculated
- [ ] **Given** performance metrics are available, **When** GET /api/v1/backtests/{id}/report is called, **Then** returns full performance report with metrics breakdown
- [ ] **Given** a backtest run, **When** viewed, **Then** results include per-instrument breakdown and aggregate performance
- [ ] **Given** performance data, **When** chart data is requested, **Then** returns time-series of cumulative returns vs buy-and-hold

## Technical Notes

- FastAPI endpoint for report access
- Generate both JSON data and chart-ready time-series
- Include confusion matrix data
- Support PDF report generation (stretch goal)

## Dependencies

### Requires
- 001-backtest-execution-engine

### Enables
- Model comparison and selection

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| No signals generated in period | Return zero accuracy, empty confusion matrix |
| Division by zero in metrics | Handle edge cases (e.g., precision when no positive predictions) |
| Outlier P&L from single trade | Flag outlier, include in aggregate |
