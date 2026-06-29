# Next‑Session Roadmap – Paper‑Trading System

## 1.  Project Snapshot

| Item | Status | Notes |
|------|--------|-------|
| **Codebase** | ✅ Scaffolded by Github‑Copilot – *minimal* FastAPI app | All core simulation logic is missing |
| **specsmd AI‑DLC** | ✅ Planning phase complete – 1 intent (`001-ai‑trading‑signals`) | 4 units, 16 stories, 9 bolts – construction ready |
| **Docker** | ✅ `docker-compose.yml` & `Dockerfile` exist | No prod/live overrides yet |
| **Tests** | 🗸 2 trivial integration tests | 0 unit/integration tests for simulator, risk engine, brokers |
| **Persistence** | ❌ Not present | No DB models / migrations |
| **Agents** | ❌ Not present | 7 AI agents (Technical, Macro, Sentiment, Bull, Bear, Trader, Risk) |
| **Telegram** | ❌ Not present | No approval flow |
| **Promotion Gate** | ❌ Not present | Will enforce 9 hard rules before go‑live |
| **Simulation Engine** | ❌ Very minimal | Only a 20‑line `PaperSimulator` with straight‑price + slippage |
| **Risk Engine** | ❌ Very minimal | Single draw‑down + cash check |
| **Broker Adapters** | ❌ Stubs | AngelOne & Groww just return a canned dict |

---

## 2.  Current Folder Structure
AI Algo Trade/ ├─ app/ │ ├─ init.py │ ├─ main.py # FastAPI entry point │ ├─ api/ │ │ ├─ health.py │ │ └─ trade.py │ ├─ sim/ # ✅ PaperSimulator (stub) │ │ └─ simulator.py │ ├─ risk/ # ✅ RiskEngine (stub) │ │ └─ engine.py │ ├─ brokers/ # ✅ Adapter stubs (AngelOne, Groww) │ │ ├─ base.py │ │ ├─ angelone.py │ │ └─ groww.py │ ├─ services/ # empty – promotion_gate.py will live here │ ├─ templates/ │ │ └─ ... │ └─ tests/ # empty – tests are in repo root ├─ tests/ │ ├─ test_health.py │ └─ test_trade.py ├─ Dockerfile ├─ docker-compose.yml ├─ requirements.txt ├─ README.md └─ next_session_plan.md (this file)


---

## 3.  What Has Been Completed (All intents and bolts are **planned**)

| Intent | Units | Stories | Bolts |
|--------|-------|---------|-------|
| `001-ai‑trading‑signals` | 4 | 16 | 9 |
| 1. Data Ingestion (BDD) | 2 | 4 | 2 |
| 2. Signal Engine | 2 | 4 | 2 |
| 3. Backtesting | 2 | 3 | 2 |
| 4. UI | 1 | 5 | 3 |

> **Why this matters** – the *specsmd* AI‑DLC workflow is now locked and ready to ship code.  
> We will systematically walk through each bolt to evolve the system from a stub to a fully‑featured paper‑trading engine.

---

## 4.  Short‑Term Goals – The Padding‑Out “Paper‑Trading” Stack

| # | What's Required | Owner | Notes |
|---|-----------------|------|-------|
| 1 | **Persistence layer** (SQLAlchemy models, Alembic migrations) | **you** | Order, Position, Signal, AuditLog + DB session helper |
| 2 | **Core configuration** (`app/core/config.py`, structured logging) | **you** | Move .env handling into a reusable settings module |
| 3 |