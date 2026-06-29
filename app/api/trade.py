"""API endpoints for portfolio, market data, signals, backtesting, and orders."""
import logging

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from app.services.orchestrator import Orchestrator

logger = logging.getLogger(__name__)
router = APIRouter()


class OrderRequest(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=20, pattern=r"^[A-Z0-9]+$")
    qty: int = Field(..., gt=0, le=100_000)
    side: str = Field(..., pattern=r"^(BUY|SELL)$")
    order_type: str = Field(default="MARKET", pattern=r"^(MARKET|LIMIT)$")
    limit_price: float | None = Field(default=None, ge=0.01)
    is_fo: bool = False


class OrderResponse(BaseModel):
    success: bool
    order_id: str | None = None
    symbol: str | None = None
    side: str | None = None
    qty_requested: int | None = None
    qty_filled: int | None = None
    price: float | None = None
    partial: bool = False
    rejection_reason: str | None = None
    latency_ms: float | None = None
    error: str | None = None
    mode: str | None = None


class SignalRequest(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=20)
    signal_type: str = Field(..., pattern=r"^(BUY|SELL|HOLD)$")
    confidence: float = Field(..., ge=0.0, le=1.0)
    price: float | None = None
    model_version: str | None = None
    rationale: str | None = None
    features: dict | None = None


class BacktestRequest(BaseModel):
    symbol: str = Field(..., min_length=1)
    model_version: str | None = "v1.0"
    start_date: str
    end_date: str


# ---- Trade ----

@router.post("/trade/execute", response_model=OrderResponse)
async def execute_trade(req: OrderRequest, request: Request):
    orch: Orchestrator = request.app.state.orchestrator
    result = await orch.execute_trade(
        symbol=req.symbol,
        qty=req.qty,
        side=req.side,
        order_type=req.order_type,
        limit_price=req.limit_price,
        is_fo=req.is_fo,
    )
    return result


# ---- Portfolio ----

@router.get("/portfolio")
async def get_portfolio(request: Request):
    orch: Orchestrator = request.app.state.orchestrator
    return orch.get_portfolio()


@router.get("/portfolio/risk")
async def get_risk_metrics(request: Request):
    orch: Orchestrator = request.app.state.orchestrator
    return orch.get_risk_metrics()


# ---- Market Data ----

@router.get("/market/prices")
async def get_market_prices(request: Request):
    orch: Orchestrator = request.app.state.orchestrator
    return {"prices": orch.get_market_prices(), "mode": orch.get_trade_mode()}


@router.get("/market/orderbook/{symbol}")
async def get_orderbook(symbol: str, request: Request):
    orch: Orchestrator = request.app.state.orchestrator
    ob = orch.simulator.get_order_book(symbol.upper())
    if not ob:
        orch.simulator.set_price(symbol.upper(), 100.0)
        ob = orch.simulator.get_order_book(symbol.upper())
    return {
        "symbol": symbol.upper(),
        "last_price": ob.last_price,
        "spread_pct": ob.spread_pct,
        "bids": [{"price": l.price, "qty": l.qty, "orders": l.orders} for l in (ob.bids or [])],
        "asks": [{"price": l.price, "qty": l.qty, "orders": l.orders} for l in (ob.asks or [])],
    }


# ---- Signals ----

@router.post("/signals/ingest")
async def ingest_signal(req: SignalRequest, request: Request):
    orch: Orchestrator = request.app.state.orchestrator
    return {"status": "accepted", "signal_id": "pending-db"}


@router.get("/signals/recent")
async def get_recent_signals(request: Request, limit: int = 50):
    try:
        from app.db.session import async_session
        from app.db.models import Signal
        from sqlalchemy import select, desc

        async with async_session() as session:
            result = await session.execute(
                select(Signal).order_by(desc(Signal.created_at)).limit(limit)
            )
            signals = result.scalars().all()
            return {
                "signals": [
                    {
                        "id": s.id,
                        "symbol": s.symbol,
                        "signal_type": s.signal_type,
                        "confidence": s.confidence,
                        "price": s.price,
                        "model_version": s.model_version,
                        "rationale": s.rationale,
                        "created_at": s.created_at.isoformat() if s.created_at else None,
                    }
                    for s in signals
                ]
            }
    except Exception:
        return {"signals": [], "note": "Database unavailable"}


# ---- Backtest ----

@router.post("/backtest/run")
async def run_backtest(req: BacktestRequest, request: Request):
    orch: Orchestrator = request.app.state.orchestrator
    from datetime import datetime
    import random

    base_price = 100.0
    sim = orch.simulator
    sim.set_price(req.symbol, base_price)

    days = 30
    price = base_price
    trades = 0
    wins = 0
    pnl = 0.0

    for day in range(days):
        change = random.gauss(0, 0.015)
        price *= (1 + change)
        sim.set_price(req.symbol, price)

        if day % 5 == 0 and day < days - 5:
            signal = 1 if change > 0 else -1
            if signal > 0:
                result = await sim.execute_order(req.symbol, 10, "BUY")
                result2 = await sim.execute_order(req.symbol, 10, "SELL")
            else:
                result = await sim.execute_order(req.symbol, 10, "SELL")
                result2 = await sim.execute_order(req.symbol, 10, "BUY")
            trades += 1
            if result2.executed_price and result.executed_price:
                trade_pnl = (result2.executed_price - result.executed_price) * 10
                pnl += trade_pnl
                if trade_pnl > 0:
                    wins += 1

    return {
        "symbol": req.symbol,
        "model_version": req.model_version,
        "days_simulated": days,
        "total_trades": trades,
        "win_rate": round(wins / trades * 100, 1) if trades > 0 else 0,
        "pnl_simulated": round(pnl, 2),
        "final_price": round(price, 2),
        "mode": "backtest",
    }


# ---- Trade Log ----

@router.get("/trades/log")
async def get_trade_log(request: Request, limit: int = 100):
    orch: Orchestrator = request.app.state.orchestrator
    log = orch.simulator.trade_log[-limit:]
    return {"trades": list(reversed(log)), "total": len(orch.simulator.trade_log)}


# ---- Dashboard summary ----

@router.get("/dashboard/summary")
async def dashboard_summary(request: Request):
    orch: Orchestrator = request.app.state.orchestrator
    portfolio = orch.get_portfolio()
    risk = orch.get_risk_metrics()
    prices = orch.get_market_prices()
    recent_signals_resp = await get_recent_signals(request, limit=10)
    return {
        "portfolio": portfolio,
        "risk": risk,
        "market_prices_sample": dict(list(prices.items())[:5]),
        "recent_signals": recent_signals_resp.get("signals", []),
        "trade_log_count": len(orch.simulator.trade_log),
        "mode": orch.mode,
    }


# ---- Mode switch ----

@router.post("/admin/mode")
async def set_trade_mode(request: Request, mode: str = "paper"):
    orch: Orchestrator = request.app.state.orchestrator
    if mode not in ("paper", "live"):
        raise HTTPException(status_code=400, detail="Mode must be 'paper' or 'live'")
    orch.mode = mode
    return {"mode": mode, "message": f"Trade mode set to {mode} (restart required for full effect)"}
