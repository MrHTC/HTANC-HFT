---
id: 004-model-versioning-ab
unit: 002-signal-engine
intent: 001-ai-trading-signals
status: draft
priority: should
created: 2026-06-18T01:37:00Z
assigned_bolt: null
implemented: false
---

# Story: 004-model-versioning-ab

## User Story

**As a** admin
**I want** to manage model versions and run A/B comparisons
**So that** I can evaluate model improvements before full rollout

## Acceptance Criteria

- [ ] **Given** a new model version is uploaded, **When** registered in the model registry, **Then** it is stored with metadata (version, architecture, training date, metrics)
- [ ] **Given** two model versions are active, **When** A/B test is configured, **Then** traffic is split between models per the configured ratio
- [ ] **Given** A/B test is running, **When** signals are generated, **Then** each signal is tagged with which model version produced it
- [ ] **Given** test results are available, **When** queried, **Then** returns comparison metrics between model versions

## Technical Notes

- Store model registry in Supabase PostgreSQL
- Model artifacts stored on filesystem or S3-compatible storage
- A/B ratio configurable via admin API
- Signal tagging enables per-version performance tracking

## Dependencies

### Requires
- 002-model-loading-inference
- 003-signal-generation-api

### Enables
- Model performance optimization

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| New model crashes | Auto-rollback to previous version |
| A/B ratio doesn't divide evenly | Use weighted random assignment |
| Both models produce same signal | Deduplicate or merge in response |
