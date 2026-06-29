from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.orchestrator import Orchestrator

router = APIRouter()

class OrderIn(BaseModel):
    symbol: str
    qty: int
    price: float = None

@router.post("/trade")
async def submit_trade(order: OrderIn):
    orch = Orchestrator()
    portfolio = {"cash": 100000}
    result = await orch.process_order(portfolio, order.dict())
    if result.get("status") == "rejected":
        raise HTTPException(status_code=400, detail=result.get("reason"))
    return result
