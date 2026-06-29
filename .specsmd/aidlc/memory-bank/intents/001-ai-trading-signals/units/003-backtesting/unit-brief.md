---
unit: 003-backtesting
intent: 001-ai-trading-signals
phase: inception
status: draft
created: 2026-06-18T01:33:00Z
updated: 2026-06-18T01:33:00Z
---

# Unit Brief: Backtesting

## Purpose
Run signal models against historical market data to measure performance, generate accuracy reports, and enable model comparison and optimization.

## Scope

### In Scope
- Running signal models against historical data
- Computing performance metrics (accuracy, precision, recall, P&L)
- Generating backtesting reports with visualizations
- Supporting configurable time periods and instrument selection
- Storing backtest results in Supabase PostgreSQL

### Out of Scope
- Real-time signal generation (handled by Signal Engine unit)
- Market data ingestion (handled by Data Ingestion unit)
- Trade execution (separate system)

---

## Assigned Requirements

| FR | Requirement | Priority |
|----|-------------|----------|
| FR-4 | Backtesting Engine - Historical performance testing | Should |

---

## Domain Concepts

### Key Entities
| Entity | Description | Attributes |
|--------|-------------|------------|
| BacktestRun | A single backtesting session | id, model_id, instrument_ids, start_date, end_date, status |
| BacktestResult | Performance results for a run | id, run_id, total_signals, correct, accuracy, precision, recall, pnl |
| PerformanceReport | Detailed breakdown of signal performance | id, result_id, period, metric, value |

### Key Operations
| Operation | Description | Inputs | Outputs |
|-----------|-------------|--------|---------|
| RunBacktest | Execute backtest for given parameters | model_id, instruments, date_range | BacktestResult |
| CompareModels | Compare performance of multiple model versions | model_ids[], date_range | Comparison report |
| GetReport | Retrieve a backtest report | run_id | PerformanceReport |
| ScheduleBacktest | Set up recurring performance evaluation | schedule_config | Scheduled job |

---

## Story Summary

| Metric | Count |
|--------|-------|
| Total Stories | 3 |
| Must Have | 2 |
| Should Have | 1 |
| Could Have | 0 |

### Stories

| Story ID | Title | Priority | Status |
|----------|-------|----------|--------|
| 001 | Backtest execution engine | Must | Planned |
| 002 | Performance metrics and reporting | Must | Planned |
| 003 | Model comparison and A/B test reports | Should | Planned |

---

## Dependencies

### Depends On
| Unit | Reason |
|------|--------|
| 001-data-ingestion | Requires historical market data for backtesting |
| 002-signal-engine | Requires signal models for evaluation |

### Depended By
| Unit | Reason |
|------|--------|
| 004-ai-trading-signals-ui | Requires backtest results for dashboard display |

### External Dependencies
None

---

## Technical Context

### Suggested Technology
- FastAPI for backtesting API
- Celery / APScheduler for async backtest job execution
- Supabase PostgreSQL for storing results
- Matplotlib / Plotly for report visualizations

### Integration Points
| Integration | Type | Protocol |
|-------------|------|----------|
| Data Ingestion | Internal | DB access |
| Signal Engine | Internal | Model inference API |
| UI | Internal | REST API |

### Data Storage
| Data | Type | Volume | Retention |
|------|------|--------|-----------|
| Backtest results | SQL (PostgreSQL) | 1K runs | 1 year |
| Performance reports | SQL (PostgreSQL) | 10K reports | 1 year |

---

## Constraints

- Backtesting must handle large historical datasets efficiently
- Results should be comparable across model versions

---

## Success Criteria

### Functional
- [ ] Backtest can run for any date range and instrument
- [ ] Performance metrics are accurate and verifiable
- [ ] Model comparison shows clear performance deltas

### Non-Functional
- [ ] Backtest for 1 year of data completes within 5 minutes
- [ ] Reports render within 2 seconds

### Quality
- [ ] Code coverage > 80%
- [ ] All acceptance criteria met

---

## Bolt Suggestions

| Bolt | Type | Stories | Objective |
|------|------|---------|-----------|
| bolt-backtesting-1 | DDD | 001 | Backtest execution engine |
| bolt-backtesting-2 | DDD | 002, 003 | Performance reporting and model comparison |
