from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.services.orchestrator import Orchestrator

router = APIRouter()


class OrderIn(BaseModel):
    symbol: str = Field(..., description="Trading symbol (e.g. RELIANCE, BTCUSD)")
    qty: int = Field(..., gt=0, description="Number of units to trade")
    price: float | None = Field(None, description="Limit price. Omit for market order.")
    side: str = Field("BUY", pattern="^(BUY|SELL)$")


@router.post("")
async def submit_trade(order: OrderIn):
    orch = Orchestrator()
    portfolio = {"cash": 100000}
    result = await orch.process_order(portfolio, order.model_dump())
    if result.get("status") == "rejected":
        raise HTTPException(status_code=400, detail=result.get("reason"))
    return result
