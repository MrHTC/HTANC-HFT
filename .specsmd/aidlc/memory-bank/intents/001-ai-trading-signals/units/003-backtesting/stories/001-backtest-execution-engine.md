---
id: 001-backtest-execution-engine
unit: 003-backtesting
intent: 001-ai-trading-signals
status: draft
priority: must
created: 2026-06-18T01:37:00Z
assigned_bolt: null
implemented: false
---

# Story: 001-backtest-execution-engine

## User Story

**As a** admin
**I want** to run backtests against historical data with specific model versions
**So that** I can evaluate model performance over time

## Acceptance Criteria

- [ ] **Given** a model version and date range, **When** a backtest is triggered, **Then** it runs the model against historical data and records all predicted signals
- [ ] **Given** a backtest is running, **When** it completes, **Then** results are stored with run_id, model_version, date_range, and signal predictions
- [ ] **Given** multiple instruments, **When** a backtest is configured with instrument list, **Then** results are computed per-instrument and aggregated
- [ ] **Given** a long-running backtest, **When** the process takes more than 30 seconds, **Then** it runs asynchronously and reports progress via status endpoint

## Technical Notes

- Use Celery or APScheduler for async backtest execution
- Reuse signal engine model inference pipeline
- Store results in Supabase PostgreSQL
- Support cancellation of in-progress backtests

## Dependencies

### Requires
- 002-signal-engine stories
- 001-data-ingestion stories

### Enables
- 002-performance-metrics-reporting

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Insufficient historical data | Return error with minimum required range |
| Backtest runs overnight | Progress tracking via status endpoint |
| Model version deleted mid-backtest | Abort with error, partial results discarded |
