from fastapi import FastAPI
from app.api.health import router as health_router
from app.api.trade import router as trade_router

app = FastAPI(title="AlgoTrade - Paper First")

app.include_router(health_router)
app.include_router(trade_router)

@app.on_event("startup")
async def startup():
    # Placeholder: init DB, redis, schedulers
    pass
