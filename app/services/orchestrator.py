"""Central orchestrator wiring paper simulator, risk engine, broker, market feed,
agents, and Telegram approval."""
import asyncio
import os
import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

from app.sim.simulator import PaperSimulator
from app.risk.engine import RiskEngine, RiskConfig
from app.brokers.base import BrokerAdapter
from app.brokers import get_broker
from app.market.feed import MarketDataFeed
from app.agents.ensemble import AgentEnsemble, SignalResult
from app.telegram.approval import TelegramApproval

logger = logging.getLogger(__name__)


class Orchestrator:
    """Coordinates all trading subsystems."""

    def __init__(self):
        self.mode = os.getenv("TRADE_MODE", "paper")

        self.simulator = PaperSimulator(
            initial_cash=float(os.getenv("PAPER_CASH", "1_000_000")),
            slippage_model=os.getenv("SLIPPAGE_MODEL", "linear"),
            fill_probability=float(os.getenv("FILL_PROBABILITY", "0.95")),
            spread_pct=float(os.getenv("SPREAD_PCT", "0.001")),
            latency_min_ms=float(os.getenv("LATENCY_MIN_MS", "50")),
            latency_max_ms=float(os.getenv("LATENCY_MAX_MS", "500")),
        )

        self.risk_engine = RiskEngine(RiskConfig(
            max_position_qty=int(os.getenv("MAX_POSITION_QTY", "5000")),
            max_notional_per_symbol=float(os.getenv("MAX_NOTIONAL", "10_000_000")),
            max_daily_loss_pct=float(os.getenv("MAX_DAILY_LOSS_PCT", "5")),
            max_drawdown_pct=float(os.getenv("MAX_DRAWDOWN_PCT", "25")),
            circuit_breaker_loss_pct=float(os.getenv("CIRCUIT_BREAKER_PCT", "3")),
            fo_max_contracts=int(os.getenv("FO_MAX_CONTRACTS", "200")),
            fo_max_exposure=float(os.getenv("FO_MAX_EXPOSURE", "5_000_000")),
        ))

        self.market = MarketDataFeed()
        self.agents = AgentEnsemble()
        self.telegram = TelegramApproval()
        self.broker: Optional[BrokerAdapter] = None
        self._running = False

        # Pre-populate default symbols
        for sym, price in [("RELIANCE", 2850), ("TCS", 3900), ("HDFCBANK", 1680),
                           ("INFY", 1580), ("ICICIBANK", 1050), ("SBIN", 760),
                           ("BHARTIARTL", 1250), ("ITC", 430), ("WIPRO", 480),
                           ("LT", 3450), ("AXISBANK", 1100), ("MARUTI", 10500),
                           ("TATAMOTORS", 950), ("NIFTY", 22450)]:
            self.simulator.set_price(sym, price)
            self.market.add_symbol(sym, price)

    async def start(self):
        self._running = True
        self.market.start()

        if self.mode == "live":
            try:
                self.broker = get_broker()
                await self.broker.connect()
                logger.info("Connected to broker: %s", os.getenv("BROKER", "angel_one"))
            except Exception as e:
                logger.error("Failed to connect broker: %s", e)
                self.mode = "paper"

        self.market.subscribe(self._on_market_update)
        logger.info("Orchestrator started in %s mode", self.mode)

    def stop(self):
        self._running = False
        self.market.stop()

    def _on_market_update(self, symbol: str, price: float):
        self.simulator.set_price(symbol, price)
        self.agents.record_price(symbol, price)
        self.risk_engine.set_drawdown(self.simulator.get_drawdown())

    def get_trade_mode(self) -> str:
        return self.mode

    async def execute_trade(
        self,
        symbol: str,
        qty: int,
        side: str,
        order_type: str = "MARKET",
        limit_price: Optional[float] = None,
        is_fo: bool = False,
        require_approval: bool = False,
        agent_name: str = "manual",
        rationale: str = "",
    ) -> dict:
        """Execute a trade through simulator or broker with full risk checks and optional approval."""

        price = limit_price or self.market.get_price(symbol) or 0
        if price <= 0:
            return {"success": False, "error": f"No market price for {symbol}"}

        portfolio_value = self.simulator.get_portfolio_value()

        risk_check = self.risk_engine.check_order(
            symbol=symbol, qty=qty, side=side, price=price,
            portfolio_value=portfolio_value,
            positions=self.simulator.positions,
            fo_positions=self.simulator.fo_positions,
            is_fo=is_fo,
            current_positions_value=portfolio_value - self.simulator.cash,
        )

        if not risk_check.passed:
            return {
                "success": False,
                "error": "; ".join(risk_check.reasons),
                "severity": risk_check.severity,
            }

        loss_check = self.risk_engine.check_daily_loss(portfolio_value)
        if not loss_check.passed:
            return {
                "success": False,
                "error": "; ".join(loss_check.reasons),
                "severity": loss_check.severity,
            }

        # Telegram approval
        if require_approval and self.telegram.is_enabled():
            trade_id = str(uuid.uuid4())
            approved = await self.telegram.request_approval(
                trade_id=trade_id,
                symbol=symbol,
                qty=qty,
                side=side,
                price=price,
                estimated_cost=price * qty,
                agent_name=agent_name,
                rationale=rationale,
            )
            if not approved:
                return {
                    "success": False,
                    "error": "Trade rejected by Telegram approval",
                    "trade_id": trade_id,
                }

        if self.mode == "live" and self.broker:
            result = await self.broker.place_order(symbol, qty, side, order_type, limit_price)
            if result.success:
                cost = (result.executed_price or 0) * (result.executed_qty or 0)
                pnl = cost if side == "SELL" else -cost
                self.risk_engine.record_trade(side, cost, pnl)
            return {
                "success": result.success,
                "order_id": result.order_id,
                "broker_order_id": result.broker_order_id,
                "status": result.status,
                "executed_price": result.executed_price,
                "executed_qty": result.executed_qty,
                "message": result.message,
                "latency_ms": result.latency_ms,
                "mode": "live",
            }

        fill = await self.simulator.execute_order(symbol, qty, side, order_type, limit_price, is_fo)

        cost = fill.avg_price * fill.qty_filled
        pnl = cost if side == "SELL" else -cost
        self.risk_engine.record_trade(side, cost, pnl if fill.qty_filled > 0 else 0)

        return {
            "success": fill.qty_filled > 0,
            "order_id": fill.order_id,
            "symbol": symbol,
            "side": side,
            "qty_requested": qty,
            "qty_filled": fill.qty_filled,
            "price": fill.avg_price,
            "partial": fill.partial,
            "rejection_reason": fill.rejection_reason,
            "latency_ms": fill.latency_ms,
            "fills": fill.fills,
            "mode": "paper",
        }

    async def analyze_and_trade(self, symbol: str) -> dict:
        """Run AI agents, get consensus signal, and execute trade."""
        signal = await self.agents.aggregate_signal(symbol)
        if signal.signal_type == "HOLD":
            return {"action": "hold", "signal": signal}

        qty = self._calculate_position_size(symbol, signal)
        if qty <= 0:
            return {"action": "hold", "reason": "position size too small", "signal": signal}

        result = await self.execute_trade(
            symbol=symbol,
            qty=qty,
            side=signal.signal_type,
            require_approval=self.telegram.is_enabled(),
            agent_name=signal.agent_name,
            rationale=signal.rationale,
        )
        result["signal"] = {
            "type": signal.signal_type,
            "confidence": signal.confidence,
            "rationale": signal.rationale,
        }
        return result

    def _calculate_position_size(self, symbol: str, signal: SignalResult) -> int:
        portfolio = self.simulator.get_portfolio_value()
        confidence = signal.confidence
        max_risk = portfolio * 0.02  # 2% risk per trade
        price = signal.price or self.market.get_price(symbol) or 100
        qty = int((max_risk * confidence) / price * 100)  # scale by confidence
        return max(qty, 0)

    def get_portfolio(self) -> dict:
        pv = self.simulator.get_portfolio_value()
        return {
            "cash": round(self.simulator.cash, 2),
            "positions_value": round(pv - self.simulator.cash, 2),
            "total_value": round(pv, 2),
            "initial_capital": self.simulator.initial_capital,
            "return_pct": round((pv - self.simulator.initial_capital) / self.simulator.initial_capital * 100, 2),
            "drawdown_pct": round(self.simulator.get_drawdown(), 2),
            "total_fees": round(self.simulator.total_fees, 2),
            "daily_pnl": round(self.simulator.get_daily_pnl(), 2),
            "positions": self.simulator.get_positions_summary(),
            "fo_positions": [
                {"symbol": k, **v}
                for k, v in self.simulator.fo_positions.items()
            ],
            "mode": self.mode,
        }

    def get_risk_metrics(self) -> dict:
        pv = self.simulator.get_portfolio_value()
        return self.risk_engine.get_risk_metrics(pv, self.simulator.positions)

    def get_market_prices(self) -> dict[str, float]:
        return self.market.get_all_prices()
