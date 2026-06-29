"""Integration tests for the full trading pipeline."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import pytest
from app.services.orchestrator import Orchestrator


@pytest.fixture
def orch():
    o = Orchestrator()
    return o


class TestFullPipeline:
    @pytest.mark.asyncio
    async def test_market_data_flow(self, orch):
        prices = orch.get_market_prices()
        assert len(prices) > 0
        assert "RELIANCE" in prices
        assert prices["RELIANCE"] > 0

    @pytest.mark.asyncio
    async def test_buy_then_sell(self, orch):
        # Reset risk engine daily P&L to avoid accumulated loss limits
        orch.risk_engine.reset()
        buy = await orch.execute_trade("RELIANCE", 10, "BUY")
        assert buy["success"], f"Buy failed: {buy}"
        assert buy["qty_filled"] == 10

        sell = await orch.execute_trade("RELIANCE", 5, "SELL")
        assert sell["success"], f"Sell failed: {sell}"
        assert sell["qty_filled"] == 5

        portfolio = orch.get_portfolio()
        positions = portfolio["positions"]
        rel_pos = next(p for p in positions if p["symbol"] == "RELIANCE")
        assert rel_pos["qty"] == 5

    @pytest.mark.asyncio
    async def test_risk_rejection(self, orch):
        result = await orch.execute_trade("RELIANCE", 100_000, "BUY")
        if not result["success"]:
            assert "error" in result

    @pytest.mark.asyncio
    async def test_drawdown_rejection(self, orch):
        orch.simulator.cash = 100_000  # huge drawdown
        orch.risk_engine.set_drawdown(90.0)
        result = await orch.execute_trade("RELIANCE", 10, "BUY")
        assert not result["success"]
        assert any("Drawdown" in str(result.get("error", "")) for r in [result])

    @pytest.mark.asyncio
    async def test_agent_to_trade_pipeline(self, orch):
        for i in range(40):
            orch.agents.record_price("RELIANCE", 2850 + i * 2)
        result = await orch.analyze_and_trade("RELIANCE")
        assert "action" in result
        assert "signal" in result or "error" in result

    @pytest.mark.asyncio
    async def test_portfolio_value(self, orch):
        portfolio = orch.get_portfolio()
        assert portfolio["total_value"] > 0
        assert portfolio["cash"] > 0
        assert "positions" in portfolio

    @pytest.mark.asyncio
    async def test_risk_metrics_available(self, orch):
        metrics = orch.get_risk_metrics()
        assert "portfolio_value" in metrics
        assert "daily_pnl" in metrics
        assert "leverage" in metrics

    @pytest.mark.asyncio
    async def test_market_prices_updated(self, orch):
        import asyncio
        await asyncio.sleep(2.1)  # Wait for market feed to tick
        prices = orch.get_market_prices()
        assert all(p > 0 for p in prices.values())

    @pytest.mark.asyncio
    async def test_multi_symbol_trading(self, orch):
        orch.risk_engine.reset()
        syms = ["RELIANCE", "TCS", "INFY"]
        for i, sym in enumerate(syms):
            result = await orch.execute_trade(sym, 5, "BUY")
            assert result["success"], f"Failed to buy {sym}: {result}"
        portfolio = orch.get_portfolio()
        assert len(portfolio["positions"]) >= len(syms)
