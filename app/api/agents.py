"""API endpoints for AI agents."""
import logging

from fastapi import APIRouter, Request

from app.services.orchestrator import Orchestrator

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/agents/analyze/{symbol}")
async def analyze_symbol(symbol: str, request: Request):
    orch: Orchestrator = request.app.state.orchestrator
    signal = await orch.agents.aggregate_signal(symbol.upper())
    agent_results = await orch.agents.analyze_symbol(symbol.upper())

    return {
        "symbol": symbol.upper(),
        "consensus": {
            "type": signal.signal_type,
            "confidence": signal.confidence,
            "price": signal.price,
            "rationale": signal.rationale,
            "model_version": signal.model_version,
        },
        "agents": [
            {
                "agent": r.agent_name,
                "signal": r.signal_type,
                "confidence": r.confidence,
                "rationale": r.rationale,
            }
            for r in agent_results
        ],
    }


@router.post("/agents/auto-trade/{symbol}")
async def auto_trade(symbol: str, request: Request):
    orch: Orchestrator = request.app.state.orchestrator
    result = await orch.analyze_and_trade(symbol.upper())
    return result


@router.get("/agents/status")
async def agent_status(request: Request):
    orch: Orchestrator = request.app.state.orchestrator
    return {
        "agents": [
            {
                "name": agent.name,
                "version": agent.version,
                "signal_count": agent.signal_count,
            }
            for agent in orch.agents.agents
        ],
        "symbols_tracked": list(orch.agents.price_history.keys()),
    }
