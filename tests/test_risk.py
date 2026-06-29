"""Tests for RiskEngine."""
import pytest
from app.risk.engine import RiskEngine, RiskConfig


@pytest.fixture
def engine():
    cfg = RiskConfig(
        max_position_qty=1000,
        max_notional_per_symbol=1_000_000,
        max_concentration_pct=20.0,
        max_leverage=3.0,
        max_daily_loss_pct=5.0,
        max_drawdown_pct=25.0,
        max_consecutive_losses=3,
        fo_max_contracts=50,
        fo_max_exposure=500_000,
        enable_circuit_breaker=False,
    )
    return RiskEngine(cfg)


class TestRiskEngine:
    def test_check_order_passes(self, engine):
        result = engine.check_order("RELIANCE", 10, "BUY", 100, 1_000_000, {})
        assert result.passed
        assert len(result.reasons) == 0

    def test_check_order_exceeds_position_limit(self, engine):
        result = engine.check_order("RELIANCE", 2000, "BUY", 100, 1_000_000, {})
        assert not result.passed
        assert any("Position qty" in r for r in result.reasons)

    def test_check_order_exceeds_notional(self, engine):
        result = engine.check_order("RELIANCE", 100, "BUY", 100_000, 1_000_000, {})
        assert not result.passed
        assert any("Notional" in r for r in result.reasons)

    def test_concentration_exceeded(self, engine):
        result = engine.check_order("RELIANCE", 1000, "BUY", 2850, 1_000_000, {})
        expected_notional = 1000 * 2850
        assert not result.passed or expected_notional <= 1_000_000 * 0.2

    def test_leverage_exceeded(self, engine):
        existing = {"EXISTING": {"qty": 10000, "avg_price": 500, "realized_pnl": 0}}
        result = engine.check_order(
            "RELIANCE", 500, "BUY", 2850, 100_000, existing, current_positions_value=5_000_000
        )
        assert not result.passed

    def test_drawdown_exceeded(self, engine):
        engine.set_drawdown(30.0)
        result = engine.check_order("RELIANCE", 50, "BUY", 100, 1_000_000, {})
        assert not result.passed
        assert any("Drawdown" in r for r in result.reasons)

    def test_fo_contract_limit(self, engine):
        result = engine.check_order("NIFTY", 100, "BUY", 22450, 1_000_000, {}, fo_positions={}, is_fo=True)
        assert not result.passed

    def test_fo_exposure_limit(self, engine):
        result = engine.check_order("NIFTY", 50, "BUY", 100_000, 1_000_000, {}, fo_positions={}, is_fo=True)
        assert not result.passed

    def test_daily_loss_limit(self, engine):
        from datetime import date
        engine.daily_pnl[date.today().isoformat()] = -100_000
        result = engine.check_daily_loss(1_000_000)
        assert not result.passed
        assert any("Daily loss" in r for r in result.reasons)

    def test_consecutive_losses(self, engine):
        engine.record_trade("SELL", 0, -100)
        engine.record_trade("SELL", 0, -200)
        engine.record_trade("SELL", 0, -150)
        assert engine.consecutive_losses == 3
        result = engine.check_daily_loss(1_000_000)
        assert not result.passed
        assert any("Consecutive" in r for r in result.reasons)

    def test_circuit_breaker(self, engine):
        engine.config.enable_circuit_breaker = True
        from datetime import date, datetime, timezone
        engine.circuit_breaker_triggered[date.today().isoformat()] = datetime.now(timezone.utc)
        result = engine.check_order("RELIANCE", 10, "BUY", 100, 1_000_000, {})
        assert not result.passed
        assert any("Circuit breaker" in r for r in result.reasons)

    def test_wins_reset_consecutive_losses(self, engine):
        engine.record_trade("SELL", 0, -100)
        engine.record_trade("BUY", 0, 50)
        assert engine.consecutive_losses == 0

    def test_risk_metrics(self, engine):
        metrics = engine.get_risk_metrics(1_000_000, {"R": {"qty": 100, "avg_price": 500, "realized_pnl": 0}})
        assert "current_drawdown_pct" in metrics
        assert "daily_pnl" in metrics
        assert "leverage" in metrics
        assert metrics["leverage"] > 0

    def test_reset(self, engine):
        engine.consecutive_losses = 5
        engine.daily_pnl["2026-01-01"] = -5000
        engine.reset()
        assert engine.consecutive_losses == 0
        assert len(engine.daily_pnl) == 0
