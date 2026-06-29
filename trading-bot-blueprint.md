# GitHub-Ready Multi-Agent Trading Bot Blueprint

## Overview

This blueprint describes a production-oriented multi-agent trading system that separates agent reasoning from deterministic validation, risk controls, and execution. Recent multi-agent trading frameworks organize specialist analyst, debate, trader, and risk roles into a coordinated workflow rather than relying on one general model to make every decision.[cite:71][cite:81][cite:85]

A production design should keep paper and live trading on nearly identical code paths, with the environment, credentials, and capital caps being the primary differences. Alpaca's API documentation explicitly supports separate paper and live environments, and agent workflow stacks commonly pair persistent state in PostgreSQL with fast coordination through Redis.[cite:90][cite:91][cite:93][cite:94]

## Recommended repository layout

```text
trading-bot/
├── README.md
├── .env.example
├── docker-compose.yml
├── pyproject.toml
├── apps/
│   └── ops-dashboard/
│       ├── app.py
│       └── pages/
├── services/
│   ├── api-gateway/
│   │   ├── main.py
│   │   ├── routes/
│   │   └── deps.py
│   ├── orchestrator/
│   │   ├── graph.py
│   │   ├── state.py
│   │   └── workers.py
│   ├── market-data/
│   │   ├── ingest.py
│   │   ├── websockets.py
│   │   └── brokers/
│   ├── alt-data/
│   │   ├── news.py
│   │   ├── events.py
│   │   └── sentiment.py
│   ├── feature-store/
│   │   ├── build_features.py
│   │   └── feature_defs.py
│   ├── agents/
│   │   ├── technical/
│   │   │   └── agent.py
│   │   ├── macro/
│   │   │   └── agent.py
│   │   ├── sentiment/
│   │   │   └── agent.py
│   │   ├── bull/
│   │   │   └── agent.py
│   │   ├── bear/
│   │   │   └── agent.py
│   │   ├── trader/
│   │   │   └── agent.py
│   │   └── risk/
│   │       └── agent.py
│   ├── validator/
│   │   ├── rules.py
│   │   ├── policy.py
│   │   └── walk_forward.py
│   ├── execution/
│   │   ├── paper.py
│   │   ├── live.py
│   │   ├── reconcile.py
│   │   └── adapters/
│   ├── backtesting/
│   │   ├── runner.py
│   │   ├── metrics.py
│   │   └── reports.py
│   └── notifications/
│       ├── telegram.py
│       └── alert_router.py
├── libs/
│   ├── broker_adapters/
│   ├── exchange_adapters/
│   ├── prompt_templates/
│   ├── schemas/
│   ├── risk_rules/
│   └── utils/
├── sql/
│   ├── migrations/
│   └── seeds/
├── infra/
│   ├── docker/
│   ├── k8s/
│   ├── terraform/
│   └── monitoring/
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── simulation/
│   └── regression/
└── docs/
    ├── architecture.md
    ├── prompts.md
    └── runbooks/
```

This layout isolates services, shared libraries, infrastructure, and tests so that prompt logic, execution logic, and risk logic can be versioned independently. That separation is important because modern stateful agent systems benefit from explicit workflow persistence and coordination rather than one large script with hidden coupling.[cite:90][cite:93][cite:99]

## Core services

| Service | Main responsibility | Recommended implementation |
|---|---|---|
| API gateway | Authentication, request routing, admin operations | FastAPI + Uvicorn [cite:99] |
| Orchestrator | Agent graph execution, checkpoints, retries, state transitions | LangGraph + Redis + PostgreSQL [cite:90][cite:93] |
| Market-data | Broker/exchange ingestion, OHLCV/ticks/account snapshots | CCXT or broker SDKs [cite:92][cite:98] |
| Alt-data | News, event calendar, sentiment ingestion | API/RSS connectors informed by analyst-agent needs [cite:71] |
| Feature-store | Standardized market and event feature packets | Python + pandas + TA pipeline |
| Agents | Technical, macro, sentiment, bull, bear, trader, risk reasoning roles | JSON-only LLM outputs [cite:71][cite:81][cite:85] |
| Validator | Hard rules, regime checks, walk-forward policy, schema enforcement | Deterministic Python rules [cite:72][cite:82] |
| Execution | Paper/live order routing, reconciliation, retries | Alpaca or broker adapters, CCXT for exchanges [cite:91][cite:94][cite:98] |
| Notifications | Alerts, paging, Telegram/Slack delivery | Telegram first, paging later |
| Ops dashboard | Human review, metrics, approvals, prompt/version control | Streamlit or lightweight web UI |

## .env.example

```dotenv
APP_ENV=dev
APP_NAME=multi-agent-trading-bot
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO

POSTGRES_DSN=postgresql://postgres:postgres@postgres:5432/trading_bot
REDIS_URL=redis://redis:6379/0

OPENAI_API_KEY=replace_me
MODEL_TECHNICAL=gpt-4.1-mini
MODEL_MACRO=gpt-4.1-mini
MODEL_SENTIMENT=gpt-4.1-mini
MODEL_TRADER=gpt-4.1
MODEL_RISK=gpt-4.1-mini

ALPACA_PAPER_API_KEY=replace_me
ALPACA_PAPER_API_SECRET=replace_me
ALPACA_PAPER_BASE_URL=https://paper-api.alpaca.markets

ALPACA_LIVE_API_KEY=replace_me
ALPACA_LIVE_API_SECRET=replace_me
ALPACA_LIVE_BASE_URL=https://api.alpaca.markets

TELEGRAM_BOT_TOKEN=replace_me
TELEGRAM_CHAT_ID=replace_me

MAX_RISK_PER_TRADE=0.005
MAX_DAILY_LOSS=0.02
MAX_SYMBOL_EXPOSURE=0.10
MAX_PORTFOLIO_DRAWDOWN=0.08
PROMOTION_MIN_PAPER_TRADES=100
PROMOTION_MIN_SHARPE=1.2
PROMOTION_MAX_PAPER_DRAWDOWN=0.06
```

Separating paper and live credentials at the environment level follows broker documentation and makes it easier to preserve one shared execution path with different deployment controls.[cite:91][cite:94]

## SQL schema starter

```sql
CREATE TABLE users (
  id UUID PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  role TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'active',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE accounts (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  broker TEXT NOT NULL,
  environment TEXT NOT NULL CHECK (environment IN ('paper','live')),
  base_currency TEXT NOT NULL DEFAULT 'USD',
  status TEXT NOT NULL DEFAULT 'active',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE symbols (
  id UUID PRIMARY KEY,
  venue TEXT NOT NULL,
  symbol TEXT NOT NULL,
  asset_class TEXT NOT NULL,
  tick_size NUMERIC,
  lot_size NUMERIC,
  UNIQUE (venue, symbol)
);

CREATE TABLE agent_runs (
  id UUID PRIMARY KEY,
  workflow_id UUID NOT NULL,
  agent_name TEXT NOT NULL,
  model TEXT NOT NULL,
  input_hash TEXT NOT NULL,
  output_json JSONB NOT NULL,
  latency_ms INT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE trade_ideas (
  id UUID PRIMARY KEY,
  workflow_id UUID NOT NULL,
  symbol_id UUID REFERENCES symbols(id),
  side TEXT NOT NULL,
  thesis_json JSONB NOT NULL,
  confidence NUMERIC NOT NULL,
  status TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE risk_decisions (
  id UUID PRIMARY KEY,
  trade_idea_id UUID REFERENCES trade_ideas(id),
  approved BOOLEAN NOT NULL,
  risk_score NUMERIC NOT NULL,
  reasons_json JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE orders (
  id UUID PRIMARY KEY,
  account_id UUID REFERENCES accounts(id),
  trade_idea_id UUID REFERENCES trade_ideas(id),
  broker_order_id TEXT,
  side TEXT NOT NULL,
  order_type TEXT NOT NULL,
  qty NUMERIC NOT NULL,
  limit_price NUMERIC,
  status TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE fills (
  id UUID PRIMARY KEY,
  order_id UUID REFERENCES orders(id),
  fill_price NUMERIC NOT NULL,
  fill_qty NUMERIC NOT NULL,
  fee NUMERIC DEFAULT 0,
  filled_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE positions (
  id UUID PRIMARY KEY,
  account_id UUID REFERENCES accounts(id),
  symbol_id UUID REFERENCES symbols(id),
  qty NUMERIC NOT NULL,
  avg_price NUMERIC NOT NULL,
  upl NUMERIC DEFAULT 0,
  rpl NUMERIC DEFAULT 0,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE backtest_runs (
  id UUID PRIMARY KEY,
  strategy_version TEXT NOT NULL,
  period_start DATE NOT NULL,
  period_end DATE NOT NULL,
  metrics_json JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

This schema focuses on auditability, versioned decisions, and traceable order flow, which is especially important in agent-driven trading systems where you need to reconstruct why a decision was made and whether a risk veto was applied.[cite:72][cite:82][cite:90]

## Sample FastAPI routes

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Multi-Agent Trading Bot")

class WorkflowRequest(BaseModel):
    symbol: str
    timeframe: str
    environment: str

@app.post("/v1/workflows/run")
async def run_workflow(req: WorkflowRequest):
    return {"status": "queued", "symbol": req.symbol, "timeframe": req.timeframe, "environment": req.environment}

@app.get("/v1/workflows/{workflow_id}")
async def get_workflow(workflow_id: str):
    return {"workflow_id": workflow_id, "status": "running"}

@app.post("/v1/risk/evaluate")
async def risk_evaluate(payload: dict):
    return {"approved": False, "reason": "placeholder"}

@app.post("/v1/orders/paper")
async def place_paper_order(payload: dict):
    return {"status": "submitted", "environment": "paper"}

@app.post("/v1/orders/live")
async def place_live_order(payload: dict):
    return {"status": "submitted", "environment": "live"}
```

FastAPI is a practical API layer for integrating agent workflows and debugging individual nodes, while paper/live routing should remain explicit at the endpoint or service-policy layer so operators can prevent accidental production crossover.[cite:91][cite:94][cite:99]

## Agent prompt JSON starter

```json
{
  "technical_analyst": {
    "system": "You are a disciplined technical analyst. Use only provided data. Return strict JSON.",
    "user_template": "Analyze {symbol} on {timeframe}. Inputs: {bars_summary}, {indicator_summary}, {volatility_summary}, {levels}. Return setup, bias, entry_zone, stop_zone, invalidators, confidence.",
    "schema": {
      "setup": "string",
      "bias": "string",
      "entry_zone": "string",
      "stop_zone": "string",
      "invalidators": ["string"],
      "confidence": "number"
    }
  },
  "trader": {
    "system": "You are a portfolio trader. Optimize risk-adjusted return, not trade count. Return strict JSON.",
    "user_template": "Inputs: {technical_report}, {macro_report}, {sentiment_report}, {bull_case}, {bear_case}, {portfolio_state}, {risk_limits}. Return action, side, qty, entry, stop, take_profit, horizon, rationale, confidence.",
    "schema": {
      "action": "string",
      "side": "string",
      "qty": "number",
      "entry": "number",
      "stop": "number",
      "take_profit": "number",
      "horizon": "string",
      "rationale": "string",
      "confidence": "number"
    }
  },
  "risk": {
    "system": "You are a hard-risk gatekeeper. Capital preservation overrides opportunity. Return strict JSON only.",
    "user_template": "Evaluate {proposed_trade} against {portfolio_state}, {daily_loss_limit}, {symbol_exposure_limit}, {correlation_limit}, {event_freeze_rules}. Return approved, risk_score, reasons, required_changes.",
    "schema": {
      "approved": "boolean",
      "risk_score": "number",
      "reasons": ["string"],
      "required_changes": ["string"]
    }
  }
}
```

JSON-only prompts and schemas make agent outputs machine-validated and are consistent with multi-agent financial workflows that route structured outputs between specialist nodes.[cite:71][cite:81][cite:85]

## Workflow graph

```text
market-data + alt-data
        ↓
feature builder
        ↓
technical / macro / sentiment agents
        ↓
bull researcher ↔ bear researcher
        ↓
trader agent
        ↓
risk validator + deterministic rules
        ↓
strategy policy gate
        ↓
paper or live execution
        ↓
reconciliation + alerts + metrics + memory update
```

A production workflow should treat the risk and policy gates as separate from the LLM debate layer, because leakage, overfitting, and unconstrained generation can make an apparently strong backtest unreliable without hard validation boundaries.[cite:72][cite:82]

## Paper-to-live promotion policy

| Rule | Suggested threshold | Reason |
|---|---|---|
| Minimum paper trades | 100+ | Small samples are noisy [cite:72] |
| Max paper drawdown | 6% | Prevent unstable strategies from graduating [cite:82] |
| Minimum Sharpe | 1.2 | Filters weak risk-adjusted performance [cite:72] |
| No critical policy violations | 0 | Risk rules must hold consistently [cite:82] |
| Live capital start | 5% or less of intended allocation | Reduces launch risk [cite:91][cite:94] |

Paper and live should share the same decision path and only diverge at credentials, endpoint, and capital limit controls, because that is the most reliable way to validate production behavior before real exposure.[cite:91][cite:94]

## Free vs paid stack choices

| Category | Free / low-cost | Paid / stronger | Why it matters |
|---|---|---|---|
| Workflow orchestration | LangGraph [cite:90][cite:93] | Managed workflow/orchestration platform [cite:96] | Stateful agent control |
| Database | PostgreSQL | Managed Postgres | Durable audit trail |
| Cache/queue | Redis OSS [cite:93] | Managed Redis | Fast coordination |
| Trading API | Alpaca paper/live [cite:91][cite:94] | Premium broker APIs | Paper/live parity |
| Exchange integration | CCXT [cite:98] | Direct institutional exchange APIs | Broad venue support |
| Monitoring | Grafana + Prometheus | Datadog / New Relic | Ops reliability |
| Alerts | Telegram | PagerDuty / Opsgenie | Faster incident response |
| Dashboard | Streamlit | Custom React/Next.js ops UI | Operator control |
| Models | Cost-efficient API models | Premium frontier models | Better reasoning where needed |

## Build order

1. Stand up PostgreSQL, Redis, and the API gateway.[cite:90][cite:93][cite:99]
2. Implement broker/exchange adapters and paper trading first.[cite:91][cite:94][cite:98]
3. Add the feature store and deterministic validator layer.[cite:72][cite:82]
4. Add analyst agents and JSON schema validation.[cite:71][cite:81][cite:85]
5. Add trader and risk agents, keeping final enforcement deterministic.[cite:82][cite:85]
6. Build reconciliation, alerts, and the ops dashboard.[cite:90][cite:91]
7. Run walk-forward and paper testing before any live promotion.[cite:72][cite:91]

## Non-negotiable safeguards

- Agent outputs should never place trades directly; execution must require deterministic approval.[cite:82]
- All prompts, strategy versions, and policy rules should be versioned in code and in the database.[cite:90]
- Historical testing should use strict time slicing and walk-forward validation because LLM systems are vulnerable to logical leakage and false confidence.[cite:72]
- Every trade should be reconstructable from agent inputs, outputs, risk decisions, and broker fills.[cite:90][cite:82]
