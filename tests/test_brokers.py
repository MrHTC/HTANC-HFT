"""Tests for broker adapters and base class."""
import pytest
from app.brokers.angel_one import AngelOneAdapter
from app.brokers.groww import GrowwAdapter


@pytest.fixture
def angel():
    return AngelOneAdapter(api_key="mock", client_id="mock", password="mock")


@pytest.fixture
def groww():
    return GrowwAdapter(api_key="mock", client_id="mock", password="mock")


class TestAngelOneAdapter:
    @pytest.mark.asyncio
    async def test_connect(self, angel):
        await angel.connect()
        assert angel.connected

    @pytest.mark.asyncio
    async def test_place_order(self, angel):
        await angel.connect()
        result = await angel.place_order("RELIANCE", 100, "BUY")
        assert result.success
        assert result.status == "FILLED"
        assert result.broker_order_id.startswith("ANGEL_")
        assert result.executed_qty == 100
        assert result.executed_price > 0

    @pytest.mark.asyncio
    async def test_place_sell_order(self, angel):
        await angel.connect()
        await angel.place_order("RELIANCE", 100, "BUY")
        result = await angel.place_order("RELIANCE", 50, "SELL")
        assert result.success
        assert result.executed_qty == 50

    @pytest.mark.asyncio
    async def test_cancel_order(self, angel):
        await angel.connect()
        result = await angel.cancel_order("nonexistent")
        assert not result

    @pytest.mark.asyncio
    async def test_get_order_status_not_found(self, angel):
        result = await angel.get_order_status("nonexistent")
        assert result.status == "NOT_FOUND"

    @pytest.mark.asyncio
    async def test_get_positions(self, angel):
        await angel.connect()
        await angel.place_order("RELIANCE", 100, "BUY")
        positions = await angel.get_positions()
        assert len(positions) > 0
        assert positions[0].symbol == "RELIANCE"
        assert positions[0].qty == 100

    @pytest.mark.asyncio
    async def test_get_balance(self, angel):
        await angel.connect()
        balance = await angel.get_balance()
        assert balance.cash > 0
        assert balance.total_equity > 0

    @pytest.mark.asyncio
    async def test_get_market_price(self, angel):
        price = await angel.get_market_price("RELIANCE")
        assert price > 0

    @pytest.mark.asyncio
    async def test_not_connected_returns_error(self, angel):
        result = await angel.place_order("RELIANCE", 10, "BUY")
        assert not result.success
        assert "Not connected" in result.message


class TestGrowwAdapter:
    @pytest.mark.asyncio
    async def test_connect(self, groww):
        await groww.connect()
        assert groww.connected

    @pytest.mark.asyncio
    async def test_place_order(self, groww):
        await groww.connect()
        result = await groww.place_order("TCS", 50, "SELL")
        assert result.success
        assert result.broker_order_id.startswith("GROWW_")
        assert result.executed_qty == 50

    @pytest.mark.asyncio
    async def test_get_balance(self, groww):
        await groww.connect()
        balance = await groww.get_balance()
        assert balance.cash > 0
