---
unit: 001-data-ingestion
intent: 001-ai-trading-signals
phase: inception
status: draft
created: 2026-06-18T01:33:00Z
updated: 2026-06-18T01:33:00Z
---

# Unit Brief: Data Ingestion

## Purpose
Ingest, normalize, and store real-time and historical market data from multiple external providers (stocks, crypto, forex) for downstream analysis and signal generation.

## Scope

### In Scope
- Connecting to multiple market data providers via a pluggable adapter pattern
- Normalizing data from different sources into a unified format
- Storing historical and real-time data in Supabase PostgreSQL
- Providing a REST API for querying market data
- Scheduling regular data fetches for real-time updates

### Out of Scope
- Signal generation and analysis (handled by Signal Engine unit)
- Backtesting and historical performance analysis (handled by Backtesting unit)
- User interface for data visualization (handled by UI unit)

---

## Assigned Requirements

| FR | Requirement | Priority |
|----|-------------|----------|
| FR-1 | Market Data Ingestion - Ingest from multiple aggregated sources | Must |

---

## Domain Concepts

### Key Entities
| Entity | Description | Attributes |
|--------|-------------|------------|
| DataSource | A configured market data provider | id, name, provider_type, api_key, enabled |
| Instrument | A tradeable financial instrument | symbol, type (stock/crypto/forex), exchange, name |
| MarketData | Price/volume data point | instrument_id, timestamp, open, high, low, close, volume |
| DataFetch | A scheduled data retrieval run | source_id, instrument_id, started_at, completed_at, status |

### Key Operations
| Operation | Description | Inputs | Outputs |
|-----------|-------------|--------|---------|
| FetchData | Retrieve latest market data from provider | source_id, instruments[] | MarketData[] |
| NormalizeData | Convert provider-specific format to unified schema | raw_data, source_type | Normalized market data |
| QueryHistory | Get historical data for an instrument | instrument_id, start, end, interval | MarketData[] |
| SubscribeRealtime | Establish WebSocket connection for streaming | source_id, instruments[] | Stream of MarketData |

---

## Story Summary

| Metric | Count |
|--------|-------|
| Total Stories | 4 |
| Must Have | 3 |
| Should Have | 1 |
| Could Have | 0 |

### Stories

| Story ID | Title | Priority | Status |
|----------|-------|----------|--------|
| 001 | Configure data sources and provider adapters | Must | Planned |
| 002 | Implement data fetching and normalization pipeline | Must | Planned |
| 003 | Build market data query API | Must | Planned |
| 004 | Real-time WebSocket data streaming | Should | Planned |

---

## Dependencies

### Depends On
| Unit | Reason |
|------|--------|
| None | First unit in dependency chain |

### Depended By
| Unit | Reason |
|------|--------|
| 002-signal-engine | Requires normalized market data for signal generation |
| 003-backtesting | Requires historical data for backtesting |
| 004-ai-trading-signals-ui | Requires market data for dashboard display |

### External Dependencies
| System | Purpose | Risk |
|--------|---------|------|
| Market Data Provider APIs | Source of price/volume data | Medium - API availability and rate limits |

---

## Technical Context

### Suggested Technology
- FastAPI for REST endpoints
- httpx for async HTTP requests to provider APIs
- Supabase PostgreSQL for data storage
- Supabase Realtime for WebSocket streaming
- Pydantic for data validation and normalization

### Integration Points
| Integration | Type | Protocol |
|-------------|------|----------|
| Provider APIs | External | REST / WebSocket |
| Signal Engine | Internal | FastAPI internal call or DB polling |
| Backtesting | Internal | DB access |
| UI | Internal | REST API |

### Data Storage
| Data | Type | Volume | Retention |
|------|------|--------|-----------|
| Market data points | SQL (PostgreSQL) | 10M+ rows/day | 90 days (tiered) |
| Data source config | SQL | < 100 rows | Indefinite |
| Instrument catalog | SQL | < 10K rows | Indefinite |

---

## Constraints

- Must support pluggable provider architecture for multiple data sources
- Data normalization must handle provider-specific quirks
- Rate limits of external providers must be respected

---

## Success Criteria

### Functional
- [ ] Data can be fetched from at least 2 different providers
- [ ] Normalized data is queryable via REST API
- [ ] Real-time streaming delivers data within 100ms of market event

### Non-Functional
- [ ] Fetch latency < 500ms per provider
- [ ] API response time p95 < 200ms

### Quality
- [ ] Code coverage > 80%
- [ ] All acceptance criteria met

---

## Bolt Suggestions

| Bolt | Type | Stories | Objective |
|------|------|---------|-----------|
| bolt-data-ingestion-1 | DDD | 001, 002 | Provider adapters and normalization |
| bolt-data-ingestion-2 | DDD | 003, 004 | Query API and real-time streaming |
