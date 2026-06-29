"""Mock Angel One broker adapter for paper/live trading simulation."""
import asyncio
import random
import uuid
from typing import Optional

from app.brokers.base import BrokerAdapter, BrokerOrderResult, BrokerPosition, BrokerBalance


class AngelOneAdapter(BrokerAdapter):
    """Angel One broker adapter (simulated for paper, configurable for live)."""

    def __init__(self, api_key: str = "", client_id: str = "", password: str = "", totp: str = ""):
        self.api_key = api_key
        self.client_id = client_id
        self.password = password
        self.totp = totp
        self.connected = False
        self.orders: dict[str, dict] = {}
        self.positions: dict[str, BrokerPosition] = {}
        self.cash = 1_000_000.0
        self.latency_range = (0.1, 0.4)  # 100-400ms

    async def connect(self):
        """Simulate broker connection."""
        if not self.api_key or self.api_key == "mock":
            await asyncio.sleep(0.05)
            self.connected = True
            return
        await asyncio.sleep(random.uniform(0.5, 1.5))
        self.connected = True

    async def place_order(
        self,
        symbol: str,
        qty: int,
        side: str,
        order_type: str = "MARKET",
        limit_price: Optional[float] = None,
    ) -> BrokerOrderResult:
        """Place an order via Angel One API (simulated)."""
        await asyncio.sleep(random.uniform(*self.latency_range))
        order_id = str(uuid.uuid4())
        broker_order_id = f"ANGEL_{order_id[:8].upper()}"

        if not self.connected:
            return BrokerOrderResult(
                success=False, order_id=order_id,
                broker_order_id=broker_order_id,
                status="REJECTED", message="Not connected to Angel One", latency_ms=0.0,
            )

        if random.random() < 0.02:  # 2% simulated rejection
            return BrokerOrderResult(
                success=False, order_id=order_id,
                broker_order_id=broker_order_id,
                status="REJECTED", message="Angel One: Order rejected (insufficient margin)",
                latency_ms=round(random.uniform(100, 400), 2),
            )

        slippage = random.uniform(-0.001, 0.001)
        executed_price = (limit_price or 100.0) * (1 + slippage)
        executed_qty = qty

        # Track position
        pos = self.positions.get(symbol, BrokerPosition(symbol=symbol, qty=0, avg_price=0.0))
        old_qty = pos.qty
        old_avg = pos.avg_price
        if side == "BUY":
            new_qty = old_qty + executed_qty
            pos.avg_price = ((old_avg * old_qty) + (executed_price * executed_qty)) / max(new_qty, 1)
            pos.qty = new_qty
        else:
            new_qty = old_qty - executed_qty
            if old_qty > 0:
                realized = (executed_price - old_avg) * executed_qty
                pos.pnl_realized += realized
            pos.qty = new_qty
        self.positions[symbol] = pos

        cost = executed_price * executed_qty
        if side == "BUY":
            self.cash -= cost
        else:
            self.cash += cost

        self.orders[order_id] = {
            "symbol": symbol, "qty": qty, "side": side, "status": "FILLED",
            "executed_price": executed_price, "executed_qty": executed_qty,
        }

        return BrokerOrderResult(
            success=True, order_id=order_id,
            broker_order_id=broker_order_id,
            status="FILLED", executed_price=round(executed_price, 2),
            executed_qty=executed_qty,
            latency_ms=round(random.uniform(100, 400), 2),
        )

    async def cancel_order(self, order_id: str) -> bool:
        await asyncio.sleep(random.uniform(0.1, 0.3))
        if order_id in self.orders and self.orders[order_id]["status"] == "PENDING":
            self.orders[order_id]["status"] = "CANCELLED"
            return True
        return False

    async def get_order_status(self, order_id: str) -> BrokerOrderResult:
        await asyncio.sleep(random.uniform(0.05, 0.15))
        order = self.orders.get(order_id)
        if not order:
            return BrokerOrderResult(
                success=False, order_id=order_id, status="NOT_FOUND", message="Order not found",
            )
        return BrokerOrderResult(
            success=True, order_id=order_id, status=order["status"],
            executed_price=order.get("executed_price"),
            executed_qty=order.get("executed_qty"),
        )

    async def get_positions(self) -> list[BrokerPosition]:
        await asyncio.sleep(random.uniform(0.1, 0.2))
        return list(self.positions.values())

    async def get_balance(self) -> BrokerBalance:
        await asyncio.sleep(random.uniform(0.1, 0.2))
        margin_used = sum(p.qty * p.avg_price for p in self.positions.values()) * 0.2
        total_equity = self.cash + sum(p.qty * p.avg_price for p in self.positions.values())
        return BrokerBalance(
            cash=round(self.cash, 2),
            margin_used=round(margin_used, 2),
            total_equity=round(total_equity, 2),
        )

    async def get_market_price(self, symbol: str) -> Optional[float]:
        await asyncio.sleep(random.uniform(0.05, 0.1))
        return round(random.uniform(50, 5000), 2)
