# Units: AI Trading Signals

## Overview

| # | Unit | Type | Dependencies | FRs |
|---|------|------|-------------|-----|
| 1 | `001-data-ingestion` | Backend (DDD) | None | FR-1 |
| 2 | `002-signal-engine` | Backend (DDD) | `001-data-ingestion` | FR-2 |
| 3 | `003-backtesting` | Backend (DDD) | `001-data-ingestion`, `002-signal-engine` | FR-4 |
| 4 | `004-ai-trading-signals-ui` | Frontend | All backend units | FR-3, FR-5 |

## Dependency Graph

```
001-data-ingestion ──► 002-signal-engine ──► 003-backtesting
         │                      │                    │
         └──────────────────────┴────────────────────┘
                              │
                        004-ai-trading-signals-ui
```

## Requirement-to-Unit Mapping

- **FR-1**: Market Data Ingestion → `001-data-ingestion`
- **FR-2**: AI Signal Generation → `002-signal-engine`
- **FR-3**: Signal Dashboard → `004-ai-trading-signals-ui`
- **FR-4**: Backtesting Engine → `003-backtesting`
- **FR-5**: Signal Notifications → `004-ai-trading-signals-ui`
