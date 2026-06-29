---
id: 004-signal-engine
unit: 002-signal-engine
intent: 001-ai-trading-signals
type: ddd-construction-bolt
status: planned
stories:
  - 003-signal-generation-api
  - 004-model-versioning-ab
created: 2026-06-18T01:38:00Z
started: null
completed: null
current_stage: null
stages_completed: []

requires_bolts:
  - 003-signal-engine
enables_bolts: []
requires_units: []
blocks: true

complexity:
  avg_complexity: 2
  avg_uncertainty: 2
  max_dependencies: 2
  testing_scope: 2
---

# Bolt: 004-signal-engine

## Overview
Second bolt for signal engine: build the signal generation API and model versioning/A/B comparison system.

## Objective
Provide REST API for signal queries and implement model versioning with A/B comparison capabilities.

## Stories Included

- **003-signal-generation-api**: Signal generation and storage API (Must)
- **004-model-versioning-ab**: Model versioning and A/B comparison (Should)

## Bolt Type

**Type**: DDD Construction Bolt
**Definition**: `.specsmd/aidlc/templates/construction/bolt-types/ddd-construction-bolt.md`

## Stages

- [ ] **1. domain-design**: Pending → domain model
- [ ] **2. logical-design**: Pending → technical design
- [ ] **3. code-generation**: Pending → implementation
- [ ] **4. testing**: Pending → test report

## Dependencies

### Requires
- 003-signal-engine (Models must be loaded and inference working)

### Enables
- UI dashboard
- Backtesting

## Success Criteria

- [ ] Signal API returns filtered, paginated signals
- [ ] Model versioning with rollback capability
- [ ] A/B comparison shows version performance
- [ ] All stories acceptance criteria met
- [ ] Tests passing
