# HTANC AI – Hyper‑Frequency Trading Engine

> **Paper‑first, AI‑powered, production‑ready.**  
> Clone, configure, and trade — in paper or live — within minutes.

[![CI](https://github.com/MrHTC/HTANC-HFT/actions/workflows/ci.yml/badge.svg)](https://github.com/MrHTC/HTANC-HFT/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Quick Start (30 seconds to paper‑trading)

```bash
git clone https://github.com/HTANC-AI/htanc-ai-hft.git
cd htanc-ai-hft
cp .env.example .env
docker compose up --build
```

Open [http://localhost:8000/health](http://localhost:8000/health) – you should see:
```json
{"status": "ok", "mode": "paper", "uptime_seconds": 12}
```

Place your first paper trade:
```bash
curl -X POST http://localhost:8000/trade \
  -H "Content-Type: application/json" \
  -d '{"symbol": "RELIANCE", "qty": 10, "price": 2500}'
```

---

## Features

| Capability | Description | Status |
|-----------|-------------|--------|
| **Paper Trading** | Built‑in simulator with configurable slippage, fees, latency, partial fills | ✅ Active |
| **Live Trading** | Broker adapters for Angel One (primary) and Groww (secondary) | 🔧 Configure |
| **Risk Engine** | F&O‑aware: position limits, margin checks, drawdown guard, circuit breaker | ✅ Active |
| **AI Signals** | Pluggable agent framework for technical, ML, and sentiment signals | 🚧 Building |
| **Telegram Approvals** | Human‑in‑the‑loop trade confirmation via Telegram bot | 🚧 Building |
| **Returns Dashboard** | REST API for P&L, position heat‑maps, performance metrics | 📊 API Ready |
| **MCP Integration** | Model Context Protocol servers for AI‑tool interaction | ✅ Configured |
| **Backtesting** | Historical replay and performance reporting | 🚧 Building |

---

## Architecture

```
┌──────────────┐     ┌────────────────┐     ┌──────────────┐
│  Telegram Bot │────▶│   FastAPI App   │◀────│  AI Agents   │
│  (Approvals)  │     │  (Trading API)  │     │  (Signals)   │
└──────────────┘     └───────┬─────────┘     └──────────────┘
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
       ┌──────────┐ ┌──────────┐ ┌──────────────┐
       │ Paper    │ │ Broker   │ │ PostgreSQL   │
       │Simulator │ │ Adapters │ │ + Redis      │
       │ (Default)│ │(AngelOne)│ │ (Persistence)│
       └──────────┘ │ (Groww)  │ └──────────────┘
                    └──────────┘
```

**Trading Modes** (set via `TRADE_MODE` env var):
- `paper` – All orders routed through the built‑in simulator. **Default & safest.**
- `live` – Orders sent to real broker APIs. Requires configured broker credentials.

---

## Configuration

### Environment Variables (`.env`)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `TRADE_MODE` | No | `paper` | `paper` or `live` |
| `DATABASE_URL` | Yes | – | PostgreSQL connection string |
| `REDIS_URL` | No | `redis://localhost:6379/0` | Redis for cache/queues |
| `TELEGRAM_BOT_TOKEN` | No | – | Telegram bot token (approvals) |
| `TELEGRAM_CHAT_ID` | No | – | Your Telegram chat ID |
| `ANGELONE_CLIENT_ID` | No* | – | Angel One client ID |
| `ANGELONE_API_KEY` | No* | – | Angel One API key |
| `ANGELONE_PASSWORD` | No* | – | Angel One trading password |
| `ANGELONE_TOTP_KEY` | No* | – | Angel One TOTP secret |
| `GROWW_CLIENT_ID` | No* | – | Groww client ID |
| `GROWW_API_KEY` | No* | – | Groww API key |
| `API_KEY` | No | – | API key for MCP endpoints |
| `LOG_LEVEL` | No | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |

*\* Required only for live trading with that broker.*

### Broker Configuration (Live Mode)

#### Angel One
1. Register at [Angel One Smart API](https://smartapi.angelbroking.com/)
2. Generate API key from the developer dashboard
3. Fill `ANGELONE_CLIENT_ID`, `ANGELONE_API_KEY`, `ANGELONE_PASSWORD`, `ANGELONE_TOTP_KEY` in `.env`
4. Set `TRADE_MODE=live` and restart

#### Groww
1. Register at [Groww API](https://groww.in/api)
2. Generate API key
3. Fill `GROWW_CLIENT_ID`, `GROWW_API_KEY` in `.env`
4. Set `TRADE_MODE=live` and restart

---

## MCP (Model Context Protocol) Integration

This repository ships with **pre‑configured MCP servers** that let AI coding tools
interact directly with your trading system. See [`mcp/README.md`](mcp/README.md).

**Available MCP endpoints:**
- `/mcp/trade` – Place, cancel, query orders
- `/mcp/market` – Real‑time & historical market data
- `/mcp/portfolio` – Positions, P&L, balances
- `/mcp/signals` – AI trading signals
- `/mcp/backtest` – Backtest execution & reports

**Supported AI tools:**
- opencode
- Claude Code (`claude mcp add ...`)
- Cursor (Settings → MCP Servers)
- VS Code + GitHub Copilot

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Service health & mode |
| `POST` | `/trade` | Place an order |
| `GET` | `/portfolio` | Current positions & P&L |
| `GET` | `/signals` | Latest AI trading signals |
| `POST` | `/backtest` | Run a backtest |
| `GET` | `/backtest/{id}` | Get backtest results |

---

## Development

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- uv (recommended) or pip

### Local Setup (without Docker)

```bash
# Install uv (optional but faster)
pip install uv

# Create virtualenv and install deps
uv venv
uv pip install -r requirements.txt

# Copy env and configure
cp .env.example .env

# Start Postgres & Redis (or use docker for just infra)
docker compose up postgres redis -d

# Run the app
uvicorn app.main:app --reload
```

### Running Tests

```bash
pytest -v --cov=app
```

### Code Quality

```bash
ruff check app/ tests/
ruff format app/ tests/ --check
```

---

## Project Structure

```
htanc-ai-hft/
├── app/
│   ├── api/          # HTTP endpoints (trade, health, portfolio)
│   ├── brokers/      # Broker adapters (Angel One, Groww)
│   ├── risk/         # F&O-aware risk engine
│   ├── sim/          # Paper simulator
│   ├── services/     # Orchestrator, Telegram, promotion gate
│   ├── schemas/      # Pydantic request/response models
│   ├── db/           # SQLAlchemy models + migrations
│   ├── agents/       # AI signal agents
│   └── main.py       # FastAPI entry point
├── mcp/              # MCP server configurations
├── scripts/          # Helper scripts
├── tests/            # Test suite
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── .env.example
```

---

## License

MIT – see [LICENSE](LICENSE).

---

## Disclaimer

**Trading involves financial risk.** This software is provided for educational
and research purposes. Past performance does not guarantee future results.
Always test thoroughly in paper mode before using with real funds.
