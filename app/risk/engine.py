"""Risk engine with F&O-aware constraints, position limits, circuit breakers."""
import math
from dataclasses import dataclass, field
from datetime import datetime, timezone, date
from typing import Optional, Callable


@dataclass
class RiskConfig:
    max_position_qty: int = 5000
    max_notional_per_symbol: float = 10_000_000.0
    max_concentration_pct: float = 20.0  # max % of portfolio per symbol
    max_leverage: float = 3.0
    max_daily_loss_pct: float = 5.0
    max_drawdown_pct: float = 25.0
    max_consecutive_losses: int = 5
    min_cash_reserve: float = 100_000.0
    circuit_breaker_loss_pct: float = 3.0  # intraday circuit breaker %
    circuit_breaker_cooldown_sec: int = 300  # 5 min cooldown
    fo_max_contracts: int = 200
    fo_max_exposure: float = 5_000_000.0
    fo_loss_limit_pct: float = 10.0  # F&O specific daily loss limit
    fo_margin_multiplier: float = 0.2  # 20% margin for F&O
    enable_circuit_breaker: bool = True


@dataclass
class RiskCheckResult:
    passed: bool = True
    reasons: list[str] = field(default_factory=list)
    severity: str = "info"  # info / warning / critical


FOPosition = dict  # {symbol, qty, avg_price, realized_pnl, expiry, is_index, lot_size}
PositionInfo = dict  # {symbol, qty, avg_price, realized_pnl}


class RiskEngine:
    """Comprehensive risk engine for F&O and equity trading."""

    def __init__(self, config: Optional[RiskConfig] = None):
        self.config = config or RiskConfig()
        self.consecutive_losses = 0
        self.daily_pnl: dict[str, float] = {}  # date -> pnl
        self.circuit_breaker_triggered: dict[str, datetime] = {}  # date -> time
        self.loss_history: list[dict] = []
        self.current_drawdown_pct = 0.0

    def set_drawdown(self, pct: float):
        self.current_drawdown_pct = pct

    # ---- Pre-trade checks ----

    def check_order(
        self,
        symbol: str,
        qty: int,
        side: str,
        price: float,
        portfolio_value: float,
        positions: dict[str, PositionInfo],
        fo_positions: dict[str, FOPosition] | None = None,
        is_fo: bool = False,
        current_positions_value: float = 0.0,
    ) -> RiskCheckResult:
        result = RiskCheckResult()

        is_long = side == "BUY"

        if is_fo:
            self._check_fo(symbol, qty, price, portfolio_value, fo_positions or {}, result)
        else:
            self._check_equity(symbol, qty, is_long, price, portfolio_value, positions, current_positions_value, result)

        self._check_global(result, portfolio_value)

        result.passed = len(result.reasons) == 0
        return result

    def _check_equity(
        self,
        symbol: str,
        qty: int,
        is_long: bool,
        price: float,
        portfolio_value: float,
        positions: dict[str, PositionInfo],
        current_positions_value: float,
        result: RiskCheckResult,
    ):
        pos = positions.get(symbol, {"qty": 0})
        new_qty = pos["qty"] + qty if is_long else pos["qty"] - qty

        # Position size limit
        if abs(new_qty) > self.config.max_position_qty:
            result.reasons.append(
                f"Position qty {abs(new_qty)} exceeds max {self.config.max_position_qty}"
            )
            result.severity = "critical"

        # Notional check
        notional = abs(new_qty) * price
        if notional > self.config.max_notional_per_symbol:
            result.reasons.append(
                f"Notional {notional:,.0f} exceeds max {self.config.max_notional_per_symbol:,.0f}"
            )
            result.severity = "critical"

        # Concentration
        if portfolio_value > 0:
            if notional > portfolio_value * self.config.max_concentration_pct / 100:
                result.reasons.append(
                    f"Concentration {notional / portfolio_value * 100:.1f}% exceeds {self.config.max_concentration_pct}%"
                )
                result.severity = "warning"

        # Leverage
        if portfolio_value > 0 and (current_positions_value + notional) / portfolio_value > self.config.max_leverage:
            result.reasons.append(
                f"Leverage exceeds max {self.config.max_leverage}x"
            )
            result.severity = "critical"

    def _check_fo(
        self,
        symbol: str,
        qty: int,
        price: float,
        portfolio_value: float,
        fo_positions: dict[str, FOPosition],
        result: RiskCheckResult,
    ):
        pos = fo_positions.get(symbol, {"qty": 0})
        new_qty = abs(pos["qty"]) + qty

        # F&O contract limit
        if new_qty > self.config.fo_max_contracts:
            result.reasons.append(
                f"F&O contracts {new_qty} exceeds max {self.config.fo_max_contracts}"
            )
            result.severity = "critical"

        # F&O exposure
        exposure = new_qty * price * self.config.fo_margin_multiplier
        if exposure > self.config.fo_max_exposure:
            result.reasons.append(
                f"F&O exposure {exposure:,.0f} exceeds max {self.config.fo_max_exposure:,.0f}"
            )
            result.severity = "critical"

        # Portfolio coverage
        if portfolio_value > 0 and exposure > portfolio_value * 0.5:
            result.reasons.append(
                f"F&O exposure {exposure / portfolio_value * 100:.1f}% of portfolio exceeds 50%"
            )
            result.severity = "warning"

    def _check_global(self, result: RiskCheckResult, portfolio_value: float):
        # Drawdown check
        if self.current_drawdown_pct > self.config.max_drawdown_pct:
            result.reasons.append(
                f"Drawdown {self.current_drawdown_pct:.1f}% exceeds max {self.config.max_drawdown_pct}%"
            )
            result.severity = "critical"

        # Circuit breaker
        today_str = date.today().isoformat()
        if today_str in self.circuit_breaker_triggered:
            triggered_at = self.circuit_breaker_triggered[today_str]
            elapsed = (datetime.now(timezone.utc) - triggered_at).total_seconds()
            if elapsed < self.config.circuit_breaker_cooldown_sec:
                remaining = int(self.config.circuit_breaker_cooldown_sec - elapsed)
                result.reasons.append(
                    f"Circuit breaker active — {remaining}s remaining"
                )
                result.severity = "critical"

    # ---- Post-trade / monitoring ----

    def record_trade(self, side: str, cost: float, pnl: float, is_fo: bool = False):
        today = date.today().isoformat()
        self.daily_pnl[today] = self.daily_pnl.get(today, 0.0) + pnl

        if pnl < 0:
            self.consecutive_losses += 1
            self.loss_history.append({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "loss": pnl,
                "side": side,
            })
        else:
            self.consecutive_losses = 0

    def check_daily_loss(self, portfolio_value: float) -> RiskCheckResult:
        result = RiskCheckResult()

        today = date.today().isoformat()
        day_pnl = self.daily_pnl.get(today, 0.0)
        loss_pct = abs(day_pnl) / portfolio_value * 100 if portfolio_value > 0 else 0

        if loss_pct > self.config.max_daily_loss_pct:
            result.reasons.append(
                f"Daily loss {loss_pct:.1f}% exceeds max {self.config.max_daily_loss_pct}%"
            )
            result.severity = "critical"
            if self.config.enable_circuit_breaker:
                self.circuit_breaker_triggered[date.today().isoformat()] = datetime.now(timezone.utc)

        if self.consecutive_losses >= self.config.max_consecutive_losses:
            result.reasons.append(
                f"Consecutive losses {self.consecutive_losses} >= {self.config.max_consecutive_losses}"
            )
            result.severity = "warning"

        result.passed = len(result.reasons) == 0
        return result

    def check_intraday_circuit_breaker(self, pnl_change_pct: float) -> RiskCheckResult:
        result = RiskCheckResult()
        if abs(pnl_change_pct) > self.config.circuit_breaker_loss_pct:
            result.reasons.append(
                f"Intraday P&L swing {pnl_change_pct:.2f}% exceeds circuit breaker {self.config.circuit_breaker_loss_pct}%"
            )
            result.severity = "critical"
            if self.config.enable_circuit_breaker:
                self.circuit_breaker_triggered[date.today().isoformat()] = datetime.now(timezone.utc)
            result.passed = False
        return result

    def get_risk_metrics(self, portfolio_value: float, positions: dict[str, PositionInfo]) -> dict:
        total_notional = sum(abs(p["qty"]) * p["avg_price"] for p in positions.values()) if positions else 0
        return {
            "current_drawdown_pct": round(self.current_drawdown_pct, 2),
            "consecutive_losses": self.consecutive_losses,
            "daily_pnl": round(self.daily_pnl.get(date.today().isoformat(), 0.0), 2),
            "total_notional": round(total_notional, 2),
            "leverage": round(total_notional / portfolio_value, 2) if portfolio_value > 0 else 0,
            "circuit_breaker_active": date.today().isoformat() in self.circuit_breaker_triggered,
            "portfolio_value": round(portfolio_value, 2),
        }

    def reset(self):
        self.consecutive_losses = 0
        self.daily_pnl.clear()
        self.circuit_breaker_triggered.clear()
        self.loss_history.clear()
        self.current_drawdown_pct = 0.0
