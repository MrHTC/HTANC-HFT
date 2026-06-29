"""HTANC AI - HFT Trading Engine entry point."""
import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.api.trade import router as trade_router
from app.api.agents import router as agents_router
from app.services.orchestrator import Orchestrator

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting HTANC AI HFT Trading Engine...")
    orch = Orchestrator()
    await orch.start()
    app.state.orchestrator = orch
    app.state.trade_mode = orch.mode
    app.state.mcp_enabled = True
    logger.info("Engine started in %s mode", orch.mode)
    yield
    logger.info("Shutting down...")
    orch.stop()


app = FastAPI(
    title="HTANC AI - HFT Trading Engine",
    description="Paper-first algorithmic trading engine with AI signals, "
    "F&O-aware risk management, and MCP integration.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router, prefix="/api", tags=["System"])
app.include_router(trade_router, prefix="/api", tags=["Trading"])
app.include_router(agents_router, prefix="/api", tags=["Agents"])
