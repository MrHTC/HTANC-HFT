---
unit: 004-ai-trading-signals-ui
intent: 001-ai-trading-signals
phase: inception
status: draft
created: 2026-06-18T01:33:00Z
updated: 2026-06-18T01:33:00Z
unit_type: frontend
default_bolt_type: simple-construction-bolt
---

# Unit Brief: AI Trading Signals UI

## Purpose
Provide a web-based dashboard for traders to view real-time trading signals, configure preferences, monitor signal performance, and receive notifications for high-confidence signals.

## Scope

### In Scope
- Real-time signal dashboard with live updates
- Signal filtering by instrument, confidence, and time range
- Performance charts and backtest result visualization
- User preferences and notification settings
- Responsive design for desktop and mobile
- Drill-down into individual signal details and rationale

### Out of Scope
- Signal generation and model management (handled by backend units)
- Market data source configuration (handled by Data Ingestion unit)
- User authentication (handled by existing Supabase Auth setup)

---

## Assigned Requirements

| FR | Requirement | Priority |
|----|-------------|----------|
| FR-3 | Signal Dashboard - Real-time UI with filtering and performance views | Must |
| FR-5 | Signal Notifications - Configurable alerts for high-confidence signals | Could |

---

## Domain Concepts

### Key UI Components
| Component | Description |
|-----------|-------------|
| SignalFeed | Real-time scrolling list of generated signals |
| SignalDetail | Expanded view of signal with rationale and supporting data |
| InstrumentSelector | Multi-select filter for instruments and markets |
| PerformanceChart | Time-series chart of signal accuracy |
| NotificationPanel | Configurable alert thresholds and delivery preferences |
| BacktestViewer | Visual display of backtest results and model comparison |

### Key User Flows
| Flow | Description |
|------|-------------|
| View Signals | See latest signals sorted by confidence, filter by instrument |
| Analyze Signal | Click a signal to see full details, model rationale, supporting indicators |
| Configure Alerts | Set confidence threshold for notifications |
| Review Performance | View accuracy charts, model comparison, backtest results |

---

## Story Summary

| Metric | Count |
|--------|-------|
| Total Stories | 4 |
| Must Have | 3 |
| Should Have | 1 |
| Could Have | 1 |

### Stories

| Story ID | Title | Priority | Status |
|----------|-------|----------|--------|
| 001 | Real-time signal feed dashboard | Must | Planned |
| 002 | Signal detail view with rationale | Must | Planned |
| 003 | Instrument filtering and search | Must | Planned |
| 004 | Performance charts and backtest visualization | Should | Planned |
| 005 | Notification settings and alerts | Could | Planned |

---

## Dependencies

### Depends On
| Unit | Reason |
|------|--------|
| 001-data-ingestion | Requires market data API for display |
| 002-signal-engine | Requires signal API for feed and details |
| 003-backtesting | Requires backtest results for performance views |

### Depended By
None (leaf unit)

### External Dependencies
| System | Purpose | Risk |
|--------|---------|------|
| Supabase Auth | User authentication | Low - already configured |

---

## Technical Context

### Suggested Technology
- Next.js (React) for frontend framework
- TypeScript for type safety
- Tailwind CSS for styling
- Chart.js / Recharts for performance charts
- Supabase Realtime for live signal updates
- Supabase Auth for authentication

### Integration Points
| Integration | Type | Protocol |
|-------------|------|----------|
| Backend API | Internal | REST (JSON) |
| WebSocket | Internal | WebSocket for real-time signals |

### Data Storage
| Data | Type | Volume | Retention |
|------|------|--------|-----------|
| User preferences | Local storage / DB | < 1KB per user | Indefinite |

---

## Constraints

- Must use existing project auth (Supabase Auth)
- Dashboard must be responsive (mobile + desktop)
- Real-time updates without page refresh

---

## Success Criteria

### Functional
- [ ] Signals display in real-time with live updates
- [ ] Users can filter by instrument, confidence, and time range
- [ ] Performance charts render from backtest data
- [ ] Notification settings persist across sessions

### Non-Functional
- [ ] Dashboard loads within 2 seconds
- [ ] Real-time updates within 500ms of signal generation
- [ ] Supports 1,000+ concurrent users

### Quality
- [ ] Code coverage > 60%
- [ ] All acceptance criteria met

---

## Bolt Suggestions

| Bolt | Type | Stories | Objective |
|------|------|---------|-----------|
| bolt-ui-1 | Simple | 001, 002 | Signal feed and detail view |
| bolt-ui-2 | Simple | 003, 004 | Filtering and performance charts |
| bolt-ui-3 | Simple | 005 | Notification settings |
