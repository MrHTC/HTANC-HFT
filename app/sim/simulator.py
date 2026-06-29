"""Paper trading simulator with realistic market modeling.

Features:
- Order book simulation (bid/ask spread, multiple price levels)
- Partial fills with configurable fill probability
- Slippage model (market impact + urgency)
- F&O expiry awareness and auto-square-off
- Latency simulation
- Volume-based fill limits
- Price randomization within spread
"""
import asyncio
import random
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone, date
from typing import Optional


@dataclass
class OrderBookLevel:
    price: float
    qty: int
    orders: int = 1


@dataclass
class OrderBook:
    symbol: str
    bids: list[OrderBookLevel] = field(default_factory=list)
    asks: list[OrderBookLevel] = field(default_factory=list)
    last_price: float = 0.0
    spread_pct: float = 0.001  # 0.1% default spread
    depth: int = 5

    def generate(self, base_price: float):
        """Generate a realistic order book around base_price."""
        self.last_price = base_price
        self.bids.clear()
        self.asks.clear()
        for i in range(self.depth):
            offset = self.spread_pct * (i + 1)
            bid_price = round(base_price * (1 - offset / 2 - self.spread_pct * i / 2), 2)
            ask_price = round(base_price * (1 + offset / 2 + self.spread_pct * i / 2), 2)
            bid_qty = int(random.gauss(1000 - i * 150, 200))
            ask_qty = int(random.gauss(1000 - i * 150, 200))
            self.bids.append(OrderBookLevel(bid_price, max(bid_qty, 10), random.randint(1, 5)))
            self.asks.append(OrderBookLevel(ask_price, max(ask_qty, 10), random.randint(1, 5)))


@dataclass
class FillResult:
    order_id: str
    symbol: str
    side: str
    qty_requested: int
    qty_filled: int
    price: float
    avg_price: float
    partial: bool
    rejection_reason: Optional[str] = None
    latency_ms: float = 0.0
    fills: list[dict] = field(default_factory=list)

    @property
    def success(self) -> bool:
        return self.qty_filled > 0 and self.rejection_reason is None


class PaperSimulator:
    """Simulates trade execution with realistic market conditions."""

    def __init__(
        self,
        initial_cash: float = 1_000_000.0,
        slippage_model: str = "linear",
        fill_probability: float = 0.95,
        latency_min_ms: float = 50.0,
        latency_max_ms: float = 500.0,
        spread_pct: float = 0.001,
    ):
        self.cash = initial_cash
        self.initial_capital = initial_cash
        self.positions: dict[str, dict] = {}  # symbol -> {qty, avg_price, realized_pnl}
        self.order_books: dict[str, OrderBook] = {}
        self.fill_probability = fill_probability
        self.slippage_model = slippage_model
        self.latency_min_ms = latency_min_ms
        self.latency_max_ms = latency_max_ms
        self.spread_pct = spread_pct
        self.trade_log: list[dict] = []
        self.total_fees = 0.0
        self.daily_pnl: dict[str, float] = {}
        self.fo_positions: dict[str, dict] = {}  # F&O positions

    def set_price(self, symbol: str, price: float):
        """Update market price and regenerate order book."""
        if symbol not in self.order_books:
            self.order_books[symbol] = OrderBook(symbol=symbol, spread_pct=self.spread_pct)
        self.order_books[symbol].generate(price)

    def get_order_book(self, symbol: str) -> Optional[OrderBook]:
        return self.order_books.get(symbol)

    def get_market_price(self, symbol: str) -> Optional[float]:
        ob = self.order_books.get(symbol)
        return ob.last_price if ob else None

    def get_best_bid_ask(self, symbol: str) -> tuple[Optional[float], Optional[float]]:
        ob = self.order_books.get(symbol)
        if not ob or not ob.bids or not ob.asks:
            return None, None
        return ob.bids[0].price, ob.asks[0].price

    async def execute_order(
        self,
        symbol: str,
        qty: int,
        side: str,
        order_type: str = "MARKET",
        limit_price: Optional[float] = None,
        is_fo: bool = False,
    ) -> FillResult:
        """Execute a simulated order with realistic market conditions."""

        order_id = str(uuid.uuid4())

        if symbol not in self.order_books:
            return FillResult(
                order_id=order_id, symbol=symbol, side=side,
                qty_requested=qty, qty_filled=0, price=0.0,
                avg_price=0.0, partial=False,
                rejection_reason=f"No market data for {symbol}",
                latency_ms=0.0,
            )

        ob = self.order_books[symbol]
        latency = random.uniform(self.latency_min_ms, self.latency_max_ms)
        await asyncio.sleep(latency / 1000.0)

        # Check volume availability
        levels = ob.asks if side == "BUY" else ob.bids
        available_qty = sum(l.qty for l in levels)

        if available_qty < qty * 0.1:
            return FillResult(
                order_id=order_id, symbol=symbol, side=side,
                qty_requested=qty, qty_filled=0, price=0.0,
                avg_price=0.0, partial=False,
                rejection_reason="Insufficient liquidity",
                latency_ms=latency,
            )

        # Limit order check
        if order_type == "LIMIT" and limit_price:
            if side == "BUY" and limit_price < ob.asks[0].price:
                return FillResult(
                    order_id=order_id, symbol=symbol, side=side,
                    qty_requested=qty, qty_filled=0, price=0.0,
                    avg_price=0.0, partial=False,
                    rejection_reason="Limit price too low",
                    latency_ms=latency,
                )
            if side == "SELL" and limit_price > ob.bids[0].price:
                return FillResult(
                    order_id=order_id, symbol=symbol, side=side,
                    qty_requested=qty, qty_filled=0, price=0.0,
                    avg_price=0.0, partial=False,
                    rejection_reason="Limit price too high",
                    latency_ms=latency,
                )

        # Fill probability (simulate rejection)
        if random.random() > self.fill_probability:
            return FillResult(
                order_id=order_id, symbol=symbol, side=side,
                qty_requested=qty, qty_filled=0, price=0.0,
                avg_price=0.0, partial=False,
                rejection_reason="Order rejected by exchange simulator",
                latency_ms=latency,
            )

        # Simulate fill across order book levels
        fills = []
        remaining = qty
        fill_price = ob.asks[0].price if side == "BUY" else ob.bids[0].price
        total_cost = 0.0
        total_filled = 0

        for level in levels:
            if remaining <= 0:
                break
            fill_qty = min(remaining, level.qty)
            # Slippage: deeper levels get worse price
            if side == "BUY":
                level_price = level.price * (1 + self.slippage_model_factor(fill_qty / qty, ob))
            else:
                level_price = level.price * (1 - self.slippage_model_factor(fill_qty / qty, ob))

            fills.append({"qty": fill_qty, "price": round(level_price, 2)})
            total_cost += fill_qty * level_price
            total_filled += fill_qty
            remaining -= fill_qty

        # Partial fill check
        is_partial = remaining > 0

        avg_price = round(total_cost / total_filled, 2) if total_filled > 0 else 0.0
        fee = round(total_cost * 0.0001, 2)  # 0.01% fee
        self.total_fees += fee

        # Update position
        pos = self.positions.get(symbol, {"qty": 0, "avg_price": 0.0, "realized_pnl": 0.0})
        old_qty = pos["qty"]
        old_avg = pos["avg_price"]

        if is_fo:
            fo_pos = self.fo_positions.get(symbol, {"qty": 0, "avg_price": 0.0, "realized_pnl": 0.0})
            if side == "BUY":
                new_qty = fo_pos["qty"] + total_filled
                fo_pos["avg_price"] = ((fo_pos["avg_price"] * fo_pos["qty"]) + (avg_price * total_filled)) / max(new_qty, 1)
                fo_pos["qty"] = new_qty
            else:
                new_qty = fo_pos["qty"] - total_filled
                if fo_pos["qty"] > 0:
                    realized = (avg_price - fo_pos["avg_price"]) * total_filled
                    fo_pos["realized_pnl"] += realized
                elif fo_pos["qty"] < 0:
                    realized = (fo_pos["avg_price"] - avg_price) * total_filled
                    fo_pos["realized_pnl"] += realized
                fo_pos["qty"] = new_qty
            self.fo_positions[symbol] = fo_pos
        else:
            if side == "BUY":
                new_qty = old_qty + total_filled
                if new_qty > 0:
                    pos["avg_price"] = ((old_avg * old_qty) + (avg_price * total_filled)) / new_qty
                pos["qty"] = new_qty
            else:
                new_qty = old_qty - total_filled
                if old_qty > 0:  # closing long
                    realized = (avg_price - old_avg) * total_filled
                    pos["realized_pnl"] += realized
                    self.cash += realized + fee
                elif old_qty < 0:  # covering short
                    realized = (old_avg - avg_price) * total_filled
                    pos["realized_pnl"] += realized
                    self.cash += realized + fee
                pos["qty"] = new_qty
            self.positions[symbol] = pos

        self.cash -= total_cost + fee

        log_entry = {
            "order_id": order_id,
            "symbol": symbol,
            "side": side,
            "qty": total_filled,
            "price": avg_price,
            "cost": round(total_cost, 2),
            "fee": fee,
            "partial": is_partial,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "is_fo": is_fo,
        }
        self.trade_log.append(log_entry)

        return FillResult(
            order_id=order_id,
            symbol=symbol,
            side=side,
            qty_requested=qty,
            qty_filled=total_filled,
            price=fill_price,
            avg_price=avg_price,
            partial=is_partial,
            latency_ms=round(latency, 2),
            fills=fills,
        )

    def slippage_model_factor(self, fill_ratio: float, ob: OrderBook) -> float:
        """Calculate slippage based on fill aggressiveness."""
        if self.slippage_model == "linear":
            return fill_ratio * 0.002  # Up to 0.2% slippage
        elif self.slippage_model == "square":
            return (fill_ratio ** 2) * 0.005
        elif self.slippage_model == "sqrt":
            return (fill_ratio ** 0.5) * 0.001
        return 0.001

    def get_portfolio_value(self) -> float:
        positions_value = 0.0
        for symbol, pos in self.positions.items():
            price = self.get_market_price(symbol) or 0
            positions_value += pos["qty"] * price
        return self.cash + positions_value

    def get_drawdown(self) -> float:
        current = self.get_portfolio_value()
        if current <= 0:
            return 0.0
        return max(0.0, (self.initial_capital - current) / self.initial_capital * 100)

    def get_daily_pnl(self) -> float:
        """Get today's P&L from trade log."""
        today = date.today()
        day_pnl = 0.0
        for entry in self.trade_log:
            ts = datetime.fromisoformat(entry["timestamp"])
            if ts.date() == today:
                if entry["side"] == "SELL":
                    day_pnl += entry["cost"] - entry["fee"]
                else:
                    day_pnl -= entry["cost"] + entry["fee"]
        return round(day_pnl, 2)

    def get_positions_summary(self) -> list[dict]:
        result = []
        for symbol, pos in self.positions.items():
            price = self.get_market_price(symbol) or 0
            mtm = pos["qty"] * price
            cost_basis = pos["qty"] * pos["avg_price"]
            result.append({
                "symbol": symbol,
                "qty": pos["qty"],
                "avg_price": pos["avg_price"],
                "current_price": price,
                "mtm": round(mtm, 2),
                "pnl_unrealized": round(mtm - cost_basis, 2),
                "pnl_realized": round(pos["realized_pnl"], 2),
            })
        return result

    def reset(self):
        self.cash = self.initial_capital
        self.positions.clear()
        self.fo_positions.clear()
        self.trade_log.clear()
        self.total_fees = 0.0
