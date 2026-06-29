import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.api.health import router as health_router
from app.api.trade import router as trade_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: connect DB, init services
    mode = os.getenv("TRADE_MODE", "paper")
    app.state.trade_mode = mode
    app.state.mcp_enabled = True
    yield
    # Shutdown: close connections


app = FastAPI(
    title="HTANC AI - HFT Trading Engine",
    description="Paper-first algorithmic trading engine with AI signals, "
    "F&O-aware risk management, and MCP integration.",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(health_router, tags=["System"])
app.include_router(trade_router, prefix="/trade", tags=["Trading"])
