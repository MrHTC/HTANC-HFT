"""Tests for PaperSimulator."""
import pytest
from app.sim.simulator import PaperSimulator, OrderBook


@pytest.fixture
def sim():
    s = PaperSimulator(initial_cash=1_000_000, fill_probability=1.0, latency_min_ms=0, latency_max_ms=0)
    s.set_price("RELIANCE", 2850.0)
    s.set_price("TCS", 3900.0)
    return s


class TestOrderBook:
    def test_generate(self):
        ob = OrderBook(symbol="TEST")
        ob.generate(100.0)
        assert len(ob.bids) == 5
        assert len(ob.asks) == 5
        assert ob.bids[0].price < 100.0
        assert ob.asks[0].price > 100.0
        assert ob.last_price == 100.0

    def test_spread(self):
        ob = OrderBook(symbol="TEST", spread_pct=0.002)
        ob.generate(100.0)
        spread = ob.asks[0].price - ob.bids[0].price
        assert 0.0 < spread < 1.0


class TestPaperSimulator:
    @pytest.mark.asyncio
    async def test_execute_buy_market(self, sim):
        result = await sim.execute_order("RELIANCE", 100, "BUY")
        assert result.success
        assert result.qty_filled == 100
        assert result.avg_price > 0
        assert sim.cash < 1_000_000
        assert sim.positions["RELIANCE"]["qty"] == 100

    @pytest.mark.asyncio
    async def test_execute_sell(self, sim):
        await sim.execute_order("RELIANCE", 100, "BUY")
        result = await sim.execute_order("RELIANCE", 50, "SELL")
        assert result.qty_filled == 50
        assert sim.positions["RELIANCE"]["qty"] == 50
        assert sim.positions["RELIANCE"]["realized_pnl"] != 0

    @pytest.mark.asyncio
    async def test_no_market_data(self, sim):
        result = await sim.execute_order("UNKNOWN", 100, "BUY")
        assert result.qty_filled == 0
        assert "No market data" in (result.rejection_reason or "")

    @pytest.mark.asyncio
    async def test_partial_fill(self, sim):
        ob = sim.order_books["RELIANCE"]
        huge_qty = sum(l.qty for l in ob.asks) * 2
        result = await sim.execute_order("RELIANCE", huge_qty, "BUY")
        assert result.qty_filled < huge_qty or result.partial

    @pytest.mark.asyncio
    async def test_limit_order_ok(self, sim):
        price = sim.get_market_price("RELIANCE")
        result = await sim.execute_order("RELIANCE", 50, "BUY", order_type="LIMIT", limit_price=price * 1.1)
        assert result.qty_filled > 0

    @pytest.mark.asyncio
    async def test_limit_order_rejected(self, sim):
        price = sim.get_market_price("RELIANCE")
        result = await sim.execute_order("RELIANCE", 50, "BUY", order_type="LIMIT", limit_price=price * 0.5)
        assert result.qty_filled == 0
        assert result.rejection_reason

    def test_portfolio_value(self, sim):
        assert sim.get_portfolio_value() == 1_000_000
        sim.cash = 715_000  # bought 100 shares at 2850
        sim.positions["RELIANCE"] = {"qty": 100, "avg_price": 2850, "realized_pnl": 0}
        sim.set_price("RELIANCE", 2850.0)
        assert sim.get_portfolio_value() == 1_000_000  # 715k cash + 285k position
        sim.set_price("RELIANCE", 3000.0)
        assert sim.get_portfolio_value() == 1_015_000  # 715k cash + 300k position

    def test_drawdown(self, sim):
        assert sim.get_drawdown() == 0.0
        sim.cash = 500_000  # lost 500k
        assert sim.get_drawdown() == 50.0

    def test_daily_pnl(self, sim):
        assert sim.get_daily_pnl() == 0.0

    def test_positions_summary(self, sim):
        sim.set_price("RELIANCE", 3000.0)
        sim.positions["RELIANCE"] = {"qty": 100, "avg_price": 2850, "realized_pnl": 500}
        summary = sim.get_positions_summary()
        assert len(summary) == 1
        assert summary[0]["symbol"] == "RELIANCE"
        assert summary[0]["pnl_unrealized"] == 15000  # (3000-2850)*100

    def test_reset(self, sim):
        sim.cash = 5000
        sim.positions["TEST"] = {"qty": 10, "avg_price": 100, "realized_pnl": 0}
        sim.reset()
        assert sim.cash == 1_000_000
        assert len(sim.positions) == 0

    @pytest.mark.asyncio
    async def test_multiple_trades(self, sim):
        await sim.execute_order("RELIANCE", 100, "BUY")
        await sim.execute_order("TCS", 50, "BUY")
        await sim.execute_order("RELIANCE", 30, "SELL")
        assert sim.positions["RELIANCE"]["qty"] == 70
        assert sim.positions["TCS"]["qty"] == 50

    @pytest.mark.asyncio
    async def test_fo_position(self, sim):
        sim.set_price("NIFTY", 22450.0)
        result = await sim.execute_order("NIFTY", 50, "BUY", is_fo=True)
        assert result.qty_filled > 0
        assert "NIFTY" in sim.fo_positions


@pytest.mark.asyncio
async def test_latency_simulation():
    s = PaperSimulator(initial_cash=1_000_000, latency_min_ms=100, latency_max_ms=200)
    s.set_price("RELIANCE", 2850.0)
    import time
    t0 = time.time()
    await s.execute_order("RELIANCE", 10, "BUY")
    elapsed = time.time() - t0
    assert elapsed >= 0.09  # at least 90ms
