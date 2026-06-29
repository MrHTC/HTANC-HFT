"""Pluggable broker adapter base class."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class BrokerOrderResult:
    success: bool
    order_id: str
    broker_order_id: Optional[str] = None
    status: str = "PENDING"
    executed_price: Optional[float] = None
    executed_qty: Optional[int] = None
    message: str = ""
    latency_ms: float = 0.0


@dataclass
class BrokerPosition:
    symbol: str
    qty: int
    avg_price: float
    pnl_unrealized: float = 0.0
    pnl_realized: float = 0.0


@dataclass
class BrokerBalance:
    cash: float = 0.0
    margin_used: float = 0.0
    total_equity: float = 0.0


class BrokerAdapter(ABC):
    """Abstract base for all broker adapters."""

    @abstractmethod
    async def place_order(
        self,
        symbol: str,
        qty: int,
        side: str,
        order_type: str = "MARKET",
        limit_price: Optional[float] = None,
    ) -> BrokerOrderResult:
        ...

    @abstractmethod
    async def cancel_order(self, order_id: str) -> bool:
        ...

    @abstractmethod
    async def get_order_status(self, order_id: str) -> BrokerOrderResult:
        ...

    @abstractmethod
    async def get_positions(self) -> list[BrokerPosition]:
        ...

    @abstractmethod
    async def get_balance(self) -> BrokerBalance:
        ...

    @abstractmethod
    async def get_market_price(self, symbol: str) -> Optional[float]:
        ...
