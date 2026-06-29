"""SQLAlchemy ORM models for the trading system."""
import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import (
    Column, String, Float, Integer, Boolean, DateTime, Text, Enum as SAEnum,
    ForeignKey, Numeric, JSON, Index,
)
from sqlalchemy.orm import relationship
from app.db.session import Base


def _utcnow():
    return datetime.now(timezone.utc)


class Order(Base):
    __tablename__ = "orders"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    symbol = Column(String(20), nullable=False, index=True)
    qty = Column(Integer, nullable=False)
    price = Column(Float, nullable=True)
    side = Column(String(4), nullable=False, default="BUY")  # BUY / SELL
    order_type = Column(String(10), nullable=False, default="MARKET")  # MARKET / LIMIT
    status = Column(String(20), nullable=False, default="PENDING")  # PENDING / FILLED / REJECTED / CANCELLED
    mode = Column(String(10), nullable=False, default="paper")  # paper / live
    executed_price = Column(Float, nullable=True)
    executed_qty = Column(Integer, nullable=True)
    cost = Column(Float, nullable=True)
    fee = Column(Float, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    broker_order_id = Column(String(100), nullable=True)
    telegram_approved = Column(Boolean, nullable=True)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    __table_args__ = (
        Index("idx_orders_symbol_created", "symbol", "created_at"),
    )


class Position(Base):
    __tablename__ = "positions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    symbol = Column(String(20), nullable=False, index=True, unique=True)
    qty = Column(Integer, nullable=False, default=0)
    avg_entry_price = Column(Float, nullable=False, default=0.0)
    current_price = Column(Float, nullable=True)
    pnl_unrealized = Column(Float, nullable=True)
    pnl_realized = Column(Float, nullable=False, default=0.0)
    side = Column(String(4), nullable=False, default="LONG")  # LONG / SHORT
    mode = Column(String(10), nullable=False, default="paper")
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)


class TradeLog(Base):
    __tablename__ = "trade_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    order_id = Column(String(36), ForeignKey("orders.id"), nullable=False)
    symbol = Column(String(20), nullable=False)
    qty = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    side = Column(String(4), nullable=False)
    cost = Column(Float, nullable=False)
    fee = Column(Float, nullable=False)
    pnl = Column(Float, nullable=True)
    mode = Column(String(10), nullable=False)
    created_at = Column(DateTime, default=_utcnow)


class Signal(Base):
    __tablename__ = "signals"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    symbol = Column(String(20), nullable=False, index=True)
    signal_type = Column(String(10), nullable=False)  # BUY / SELL / HOLD
    confidence = Column(Float, nullable=False, default=0.0)
    price = Column(Float, nullable=True)
    model_version = Column(String(50), nullable=True)
    rationale = Column(Text, nullable=True)
    features = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=_utcnow)


class PortfolioSnapshot(Base):
    __tablename__ = "portfolio_snapshots"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    cash = Column(Float, nullable=False, default=0.0)
    positions_value = Column(Float, nullable=False, default=0.0)
    total_value = Column(Float, nullable=False, default=0.0)
    pnl_day = Column(Float, nullable=True)
    pnl_total = Column(Float, nullable=True)
    drawdown_pct = Column(Float, nullable=True)
    mode = Column(String(10), nullable=False, default="paper")
    created_at = Column(DateTime, default=_utcnow)


class BacktestRun(Base):
    __tablename__ = "backtest_runs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    model_version = Column(String(50), nullable=True)
    instruments = Column(JSON, nullable=True)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    status = Column(String(20), nullable=False, default="PENDING")
    accuracy = Column(Float, nullable=True)
    precision = Column(Float, nullable=True)
    recall = Column(Float, nullable=True)
    f1_score = Column(Float, nullable=True)
    total_signals = Column(Integer, nullable=True)
    pnl_simulated = Column(Float, nullable=True)
    report = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=_utcnow)
    completed_at = Column(DateTime, nullable=True)
