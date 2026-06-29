from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/health")
async def health(request: Request):
    return {
        "status": "ok",
        "mode": getattr(request.app.state, "trade_mode", "paper"),
        "uptime_seconds": 0,
        "version": "1.0.0",
    }
