---
unit: 002-signal-engine
intent: 001-ai-trading-signals
phase: inception
status: draft
created: 2026-06-18T01:33:00Z
updated: 2026-06-18T01:33:00Z
---

# Unit Brief: Signal Engine

## Purpose
Apply deep learning models (LSTM/transformers) to normalized market data to generate buy/sell/hold trading signals with confidence scores, timestamps, and supporting rationale.

## Scope

### In Scope
- Loading and running deep learning models for inference
- Generating trading signals from market data features
- Producing signals with confidence scores, rationale, and metadata
- Storing signal history in Supabase PostgreSQL
- Providing REST API for signal queries
- Model versioning and A/B comparison

### Out of Scope
- Model training pipeline (initial models trained offline)
- Market data ingestion and normalization (handled by Data Ingestion unit)
- User interface (handled by UI unit)
- Trade execution (separate system)

---

## Assigned Requirements

| FR | Requirement | Priority |
|----|-------------|----------|
| FR-2 | AI Signal Generation - Deep learning model inference | Must |

---

## Domain Concepts

### Key Entities
| Entity | Description | Attributes |
|--------|-------------|------------|
| Model | A trained deep learning model | id, name, version, architecture, status |
| Signal | A generated trading recommendation | id, instrument_id, timestamp, type, confidence, rationale |
| FeatureSet | Computed features fed into models | id, instrument_id, timestamp, feature_vector |
| SignalResult | Performance tracking of signal outcomes | signal_id, actual_outcome, accuracy |

### Key Operations
| Operation | Description | Inputs | Outputs |
|-----------|-------------|--------|---------|
| GenerateSignal | Run model inference on latest market data | instrument_id, model_id | Signal with confidence score |
| BatchGenerate | Generate signals for multiple instruments | instrument_ids[], model_id | Signal[] |
| GetSignals | Query recent signals by instrument/filters | instrument_id, limit, min_confidence | Signal[] |
| LoadModel | Load a specific model version into memory | model_id | Loaded model reference |

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
| 001 | Feature computation pipeline from market data | Must | Planned |
| 002 | Model loading and inference engine | Must | Planned |
| 003 | Signal generation and storage API | Must | Planned |
| 004 | Model versioning and A/B comparison | Should | Planned |

---

## Dependencies

### Depends On
| Unit | Reason |
|------|--------|
| 001-data-ingestion | Requires normalized market data for feature computation |

### Depended By
| Unit | Reason |
|------|--------|
| 003-backtesting | Requires stored signals for historical performance evaluation |
| 004-ai-trading-signals-ui | Requires signals for dashboard display |

### External Dependencies
| System | Purpose | Risk |
|--------|---------|------|
| Model registry (local filesystem/S3) | Store trained model artifacts | Low |

---

## Technical Context

### Suggested Technology
- FastAPI for inference API
- PyTorch or TensorFlow for model inference
- ONNX for model serialization and optimization
- Supabase PostgreSQL for signal storage
- Pydantic for signal schema validation

### Integration Points
| Integration | Type | Protocol |
|-------------|------|----------|
| Data Ingestion | Internal | REST API or DB |
| Backtesting | Internal | DB access |
| UI | Internal | REST API |

### Data Storage
| Data | Type | Volume | Retention |
|------|------|--------|-----------|
| Signals | SQL (PostgreSQL) | 100K+/day | 1 year |
| Model metadata | SQL | < 100 rows | Indefinite |
| Feature cache | In-memory/Redis | Varies | Short-lived |

---

## Constraints

- Inference must complete within 500ms per instrument
- Models loaded into memory with efficient GPU/CPU resource management
- Backward compatibility: new model versions must maintain API contract

---

## Success Criteria

### Functional
- [ ] Signals generated for stocks, crypto, and forex
- [ ] Confidence scores and rationale included with each signal
- [ ] Model versioning with rollback capability

### Non-Functional
- [ ] Signal generation latency < 1 second end-to-end
- [ ] Supports 100+ instruments simultaneously

### Quality
- [ ] Code coverage > 80%
- [ ] All acceptance criteria met

---

## Bolt Suggestions

| Bolt | Type | Stories | Objective |
|------|------|---------|-----------|
| bolt-signal-engine-1 | DDD | 001, 002 | Feature pipeline and model inference |
| bolt-signal-engine-2 | DDD | 003, 004 | Signal API and model versioning |
