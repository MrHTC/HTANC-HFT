"""Broker adapter factory."""
import os
from typing import Optional

from app.brokers.base import BrokerAdapter
from app.brokers.angel_one import AngelOneAdapter
from app.brokers.groww import GrowwAdapter


def get_broker(broker_name: Optional[str] = None) -> BrokerAdapter:
    """Get the configured broker adapter."""
    broker = broker_name or os.getenv("BROKER", "angel_one")

    if broker == "angel_one":
        adapter = AngelOneAdapter(
            api_key=os.getenv("ANGEL_API_KEY", "mock"),
            client_id=os.getenv("ANGEL_CLIENT_ID", "mock"),
            password=os.getenv("ANGEL_PASSWORD", "mock"),
            totp=os.getenv("ANGEL_TOTP", ""),
        )
    elif broker == "groww":
        adapter = GrowwAdapter(
            api_key=os.getenv("GROWW_API_KEY", "mock"),
            client_id=os.getenv("GROWW_CLIENT_ID", "mock"),
            password=os.getenv("GROWW_PASSWORD", "mock"),
        )
    else:
        raise ValueError(f"Unknown broker: {broker}")

    return adapter
