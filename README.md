# AlgoTrade — Paper-First Trading Engine

Opinionated starter for algorithmic trading research and safe paper-mode execution.

Core features
- FastAPI HTTP API (async-first)
- Postgres for persistent storage
- Redis for cache/locks/queues
- Docker + docker-compose for local dev and testing
- Paper-mode default: built-in custom simulator for market replay and order matching
- Broker adapters: Angel One (primary) and Groww (secondary) — adapter pattern, pluggable
- F&O-aware risk engine with position limits, margin checks and greeks-aware constraints
- Telegram approval flow for human-in-the-loop trade confirmations
- Tests (pytest) and CI-friendly layout

Principles
- Paper-first: every execution defaults to a simulator unless explicitly set to live.
- Small, testable components: brokers, risk engine, and simulator are interchangeable.
- Safety-first risk checks before any live order.

Repository layout (created by scaffolder)

- `app/` — FastAPI application package
- `app/brokers/` — broker adapters (angelone, groww)
- `app/sim/` — custom paper simulator and market feed
- `app/risk/` — F&O-aware risk engine
- `app/api/` — HTTP routes and telegram approval hooks
- `tests/` — pytest test suite
- `docker-compose.yml` — dev-compose with Postgres + Redis + web
- `Dockerfile` — app image
- `.env.example` — environment variables example
- `docs/NEXT_STEPS.md` — planning and next tasks

Quickstart (local)

1. Copy example env and tweak values:

```powershell
Copy-Item .env.example .env
```

2. Build and start services with Docker Compose:

```powershell
docker-compose up --build
```

3. Open the health route in your browser (first smoke test):

http://localhost:8000/health

Development notes
- Paper (simulator) vs Live: `TRADE_MODE=paper|live` — default `paper`.
- Broker credentials are loaded from env — see `.env.example` for keys.
- Telegram approvals use `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` from env.

Testing

Run unit tests with pytest (recommended in a virtualenv or container):

```powershell
pip install -r requirements.txt
pytest -q
```

First test route

- `GET /health` — returns 200 and basic service info. Open:

http://localhost:8000/health

Operational tips
- Start services via `docker-compose` for realistic local testing (Postgres + Redis).
- Use the simulator for strategy development: it supports order book replay, execution latency simulation, and slippage parameters.

Contributing
- Follow the code style in `app/` and add tests to `tests/` for new logic.

License
- MIT
