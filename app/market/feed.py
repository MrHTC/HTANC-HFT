"""Market data feed that simulates real-time price updates."""
import asyncio
import math
import random
from datetime import datetime, timezone
from typing import Callable, Optional

PriceCallback = Callable[[str, float], None]


class MarketDataFeed:
    """Simulates real-time market data for paper trading."""

    def __init__(self, symbols: list[str] | None = None):
        self.symbols: set[str] = set(symbols or [])
        self.prices: dict[str, float] = {}
        self.volumes: dict[str, int] = {}
        self.base_prices: dict[str, float] = {}
        self.callbacks: list[PriceCallback] = []
        self.running = False
        self._task: Optional[asyncio.Task] = None
        self.update_interval = 1.0
        self.volatility: dict[str, float] = {}

    def add_symbol(self, symbol: str, base_price: float, volatility: float = 0.002):
        self.symbols.add(symbol)
        self.base_prices[symbol] = base_price
        self.prices[symbol] = base_price
        self.volumes[symbol] = random.randint(100_000, 10_000_000)
        self.volatility[symbol] = volatility

    def subscribe(self, callback: PriceCallback):
        self.callbacks.append(callback)

    def start(self):
        if not self.running:
            self.running = True
            self._task = asyncio.create_task(self._run())

    def stop(self):
        self.running = False
        if self._task:
            self._task.cancel()

    async def _run(self):
        drift = 0.0
        while self.running:
            await asyncio.sleep(self.update_interval)
            now = datetime.now(timezone.utc)
            hour = now.hour
            minute = now.minute

            # Market hours (9:15 AM - 3:30 PM IST = 3:45 AM - 10:00 AM UTC)
            is_market_hours = 3 <= hour < 10 or (hour == 3 and minute >= 45) or (hour == 10 and minute <= 0)

            for symbol in list(self.symbols):
                base = self.base_prices.get(symbol, 100.0)
                vol = self.volatility.get(symbol, 0.002)

                if is_market_hours:
                    vol_mult = 1.0
                else:
                    vol_mult = 0.2  # reduced volatility outside market hours

                # Random walk with mean reversion
                drift += random.gauss(0, vol * vol_mult)
                drift *= 0.99  # mean reversion
                noise = random.gauss(0, vol * vol_mult)
                change = base * (drift + noise)

                current = self.prices.get(symbol, base)
                new_price = max(current + change, base * 0.8)  # don't go below 80% of base
                new_price = min(new_price, base * 1.2)  # don't exceed 120% of base

                self.prices[symbol] = round(new_price, 2)

                # Volume decay and refresh
                self.volumes[symbol] = max(
                    int(self.volumes[symbol] * 0.95 + random.gauss(0, 5000)),
                    1000,
                )

            # Notify callbacks
            for cb in self.callbacks:
                for symbol in list(self.symbols):
                    try:
                        cb(symbol, self.prices[symbol])
                    except Exception:
                        pass

    def get_price(self, symbol: str) -> Optional[float]:
        return self.prices.get(symbol)

    def get_all_prices(self) -> dict[str, float]:
        return dict(self.prices)
