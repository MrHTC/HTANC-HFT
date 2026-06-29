"""Tests for AI agent ensemble."""
import pytest
from app.agents.ensemble import (
    TechnicalAgent, MacroAgent, SentimentAgent,
    BullAgent, BearAgent, TraderAgent, RiskAgent,
    AgentEnsemble,
)


def make_prices(base=100, n=30, trend=0):
    """Generate test price series with optional trend."""
    prices = []
    p = base
    for i in range(n):
        p += trend + (i % 7 - 3) * 0.5
        prices.append(max(p, 10))
    return prices


class TestTechnicalAgent:
    @pytest.mark.asyncio
    async def test_bullish_signal(self):
        agent = TechnicalAgent()
        prices = [30, 28, 26, 25, 24, 23, 22, 21, 20, 19, 18, 17, 16, 15, 20, 25, 30, 35, 38, 40]
        result = await agent.analyze("TEST", 42, prices)
        assert result.agent_name == "Technical"

    @pytest.mark.asyncio
    async def test_insufficient_data(self):
        agent = TechnicalAgent()
        result = await agent.analyze("TEST", 100, [100, 101])
        assert result.signal_type == "HOLD"


class TestMacroAgent:
    @pytest.mark.asyncio
    async def test_bullish_macro(self):
        agent = MacroAgent()
        prices = [100 + i * 1.5 for i in range(15)]  # strong uptrend
        result = await agent.analyze("TEST", prices[-1], prices)
        assert result.signal_type in ("BUY", "HOLD")


class TestSentimentAgent:
    @pytest.mark.asyncio
    async def test_returns_signal(self):
        agent = SentimentAgent()
        prices = make_prices()
        result = await agent.analyze("TEST", 100, prices)
        assert result.agent_name == "Sentiment"
        assert result.signal_type in ("BUY", "SELL", "HOLD")


class TestBullAgent:
    @pytest.mark.asyncio
    async def test_bullish_momentum(self):
        agent = BullAgent()
        prices = [100, 101, 102, 103, 105, 108]
        result = await agent.analyze("TEST", 110, prices)
        assert result.signal_type in ("BUY", "HOLD")

    @pytest.mark.asyncio
    async def test_insufficient_data(self):
        agent = BullAgent()
        result = await agent.analyze("TEST", 100, [100])
        assert result.signal_type == "HOLD"


class TestBearAgent:
    @pytest.mark.asyncio
    async def test_bearish_reversion(self):
        agent = BearAgent()
        prices = [100] * 9 + [120]  # sharp spike
        result = await agent.analyze("TEST", 115, prices)
        assert result.signal_type in ("SELL", "HOLD")


class TestTraderAgent:
    @pytest.mark.asyncio
    async def test_breakout_detection(self):
        agent = TraderAgent()
        prices = [100, 100.5, 99.5, 100, 100.3, 105]  # breakout
        result = await agent.analyze("TEST", 105, prices)
        assert result.signal_type in ("BUY", "HOLD")


class TestRiskAgent:
    @pytest.mark.asyncio
    async def test_high_volatility(self):
        agent = RiskAgent()
        # High volatility prices
        prices = [100]
        for _ in range(25):
            prices.append(prices[-1] * (1 + (-0.03 if _ % 2 == 0 else 0.03)))
        result = await agent.analyze("TEST", prices[-1], prices)
        assert result.agent_name == "Risk"


class TestAgentEnsemble:
    @pytest.mark.asyncio
    async def test_ensemble_runs_all_agents(self):
        ensemble = AgentEnsemble()
        for i in range(30):
            ensemble.record_price("RELIANCE", 2850 + i * 5)
        results = await ensemble.analyze_symbol("RELIANCE")
        assert len(results) == 7
        agent_names = {r.agent_name for r in results}
        assert agent_names == {"Technical", "Macro", "Sentiment", "Bull", "Bear", "Trader", "Risk"}

    @pytest.mark.asyncio
    async def test_aggregate_signal(self):
        ensemble = AgentEnsemble()
        for i in range(40):
            ensemble.record_price("RELIANCE", 2850 + i * 3)
        signal = await ensemble.aggregate_signal("RELIANCE")
        assert signal.signal_type in ("BUY", "SELL", "HOLD")
        assert 0.0 <= signal.confidence <= 1.0
        assert signal.agent_name == "Ensemble"

    @pytest.mark.asyncio
    async def test_empty_symbol(self):
        ensemble = AgentEnsemble()
        signal = await ensemble.aggregate_signal("UNKNOWN")
        assert signal.symbol == "UNKNOWN"
