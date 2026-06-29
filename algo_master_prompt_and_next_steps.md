# AlgoAI Master Prompt + Next Steps

## Master prompt

```text
Use only the existing file `trading-bot-blueprint.md` as the source of truth.

Goal: generate the complete repo end-to-end with minimum hassle, minimum tokens, and best file organization for a production-oriented multi-agent AlgoAI trader in Python.

Context:
- primary_broker=angelone
- secondary_broker=groww
- markets=crypto+indian_stocks+options+futures
- execution_mode=paper_first_then_semi_auto_live
- live_approval=telegram_manual_required
- simulator=custom_required
- initial_live_capital_inr=10000
- capital_update=manual_user_control
- risk_per_trade=0.5%
- max_daily_loss=2%
- max_drawdown=6%
- leverage_limit=1x_to_2x
- stack=fastapi+postgres+redis+docker
- ide=vscode+copilot
- deployment=laptop_first+cloud_ready
- priority=robustness>profit_claims>speed
- token_mode=minimal

Non-negotiable rules:
1. Use `trading-bot-blueprint.md` only; do not ask for more architecture clarification unless absolutely blocking.
2. Generate all required files with best folder structure and production-safe organization.
3. LLMs analyze only; deterministic code handles sizing, margin, exposure, risk checks, validation, approvals, routing, reconciliation.
4. Paper mode is default and fail-closed.
5. No live routing until promotion gate passes.
6. Promotion gate = min 100 paper trades, min 6 paper days, positive expectancy after fees and slippage, max drawdown < 6%, zero critical reconciliation or execution failures.
7. Custom simulator must model spread, slippage, latency, partial fills, fees, and F&O specifics.
8. All agent outputs must be compact strict JSON with schemas.
9. Agents run only on bar close, event trigger, or explicit signal trigger.
10. Angel One live deployment must be static-IP-ready.
11. Respect Groww API rate limits with throttling and retry.
12. Initial live capital cap must be configurable and default to INR 10000.
13. Keep prompts, logs, and outputs compact; no filler.
14. No placeholders like TODO, FIXME, or "implement later".

Required repo structure:
- app/core
- app/db
- app/brokers
- app/paper
- app/risk
- app/agents
- app/services
- app/schemas
- app/api
- tests
- docs

Required outputs:
1. repo tree
2. full contents of every starter file needed for a working paper-trading system
3. setup commands
4. local run commands
5. docker run commands
6. test commands
7. exact implementation order
8. exact paper-to-live promotion flow
9. one file `docs/NEXT_STEPS.md` with the user’s exact next actions

Core deliverables:
- README.md
- .env.example
- requirements.txt
- Dockerfile
- docker-compose.yml
- app/main.py
- config, logging, constants
- db models and session
- broker base + angelone + groww adapters
- custom paper simulator
- F&O-aware risk engine
- telegram approval flow
- reconciliation service
- promotion gate
- tests

Output style:
- concise
- code first
- complete files only
- minimum explanation
- best organization
```

## Exact next steps

### 1) Best paper-testing route

Use the bot’s own custom paper simulator as the main truth source, and optionally compare your manual strategy intuition against an Indian derivatives-focused paper app such as NeoStox-style simulators for F&O practice, because third-party paper apps can help you sanity-check execution assumptions but should not replace your own simulator’s audit trail.[cite:200]

If you want a second external benchmark app for quick habit-building, Tradetron-style paper environments are useful for real-time market simulation across multiple asset classes, but they are better as a comparison layer than as the core engine for your own bot.[cite:196]

### 2) Best initial paper configuration

Start with paper-only mode, initial virtual capital of INR 10000, leverage capped at 1x for the first test week, and only after stable logs move to 1.5x to 2x in simulator runs, because leverage magnifies both mistakes and false confidence.[cite:200]

Paper test only these instruments first:
- NIFTY liquid options
- one NIFTY future setup
- one or two highly liquid equity names
- BTC/ETH only if you have a separate clean feed and strategy path

### 3) Exact paper test sequence

1. Run the repo locally in paper mode only.
2. Verify health route, DB writes, Redis connectivity, and Telegram alerts.
3. Run 20 dry test signals with mock data.
4. Run 10 market-session paper trades manually approved through Telegram.
5. Check fills, slippage, fees, partial fills, and position reconciliation.
6. Expand to 100 paper trades over at least 6 paper days.
7. Measure expectancy after fees/slippage, win rate, average loss, max drawdown, and execution errors.
8. Do not go live unless promotion gate passes.

### 4) Exact success metrics before live

Require all of these:
- at least 100 paper trades
- at least 6 paper days
- positive expectancy after fees and slippage
- max drawdown below 6%
- no critical reconciliation mismatch
- no order-state sync failure
- Telegram approvals working on every candidate live-style trade

### 5) Best live route after your order

After you explicitly approve going live, keep Angel One as primary and Groww as fallback, but deploy from a static-IP-ready environment because Angel One requires API order execution to originate from a registered primary static IP for self-coded algorithms from April 1, 2026.[cite:167]

Groww should remain secondary with throttling because its rate limits are grouped by API type, including 10 requests per second for Orders and 10 per second for Live Data in the published developer docs.[cite:138]

### 6) Initial real-money setup

Start live with max usable capital capped at INR 10000 and keep that cap as an environment variable you can change later. Do not let the bot auto-scale capital without manual update.

Suggested live ramp:
1. INR 10000 cap, 1x leverage, very small position size.
2. 2 weeks stable reconciliation and controlled drawdown.
3. Increase capital only manually.
4. Keep manual Telegram approval mandatory.

### 7) Deployment advice

Use laptop for development, then move paper mode to a cheap cloud VM, then move live mode only to a static-IP setup because local dynamic-IP execution is risky for Angel One live compliance under the 2026 framework.[cite:167]

### 8) What to test for profit quality

Track these in `docs/NEXT_STEPS.md` and in the DB:
- expectancy per trade
- net PnL after fees/slippage
- profit factor
- max drawdown
- average adverse excursion
- slippage by symbol
- approval-to-execution latency
- reconciliation error count

High win rate alone is not enough; expectancy after costs matters more for real survivability.
