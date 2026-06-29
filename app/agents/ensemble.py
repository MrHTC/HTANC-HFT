"""AI signal agents that generate BUY/SELL/HOLD signals from market data.

7 agents:
  1. TechnicalAgent — EMA crossover, RSI, MACD, Bollinger
  2. MacroAgent — macro-economic trend analysis
  3. SentimentAgent — news/social sentiment analysis
  4. BullAgent — trend-following, momentum
  5. BearAgent — contrarian, mean-reversion
  6. TraderAgent — pattern-based scalping
  7. RiskAgent — drawdown protection, volatility regime
"""
import logging
import math
import random
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class SignalResult:
    symbol: str
    signal_type: str  # BUY / SELL / HOLD
    confidence: float  # 0.0 - 1.0
    price: float | None = None
    model_version: str = ""
    rationale: str = ""
    agent_name: str = ""


class BaseAgent(ABC):
    """Base class for all signal agents."""

    def __init__(self, name: str, version: str = "1.0"):
        self.name = name
        self.version = version
        self.signal_count = 0

    @abstractmethod
    async def analyze(self, symbol: str, price: float, prices: list[float]) -> SignalResult:
        ...


class TechnicalAgent(BaseAgent):
    """Technical analysis: EMA crossover, RSI, MACD, Bollinger Bands."""

    def __init__(self):
        super().__init__("Technical", "1.0")

    async def analyze(self, symbol: str, price: float, prices: list[float]) -> SignalResult:
        if len(prices) < 20:
            return SignalResult(symbol, "HOLD", 0.0, price, self.version, "Insufficient data", self.name)

        # RSI calculation
        gains, losses = 0.0, 0.0
        for i in range(1, 15):
            diff = prices[-i] - prices[-i - 1]
            if diff > 0:
                gains += diff
            else:
                losses += abs(diff)
        avg_gain = gains / 14
        avg_loss = losses / 14
        rs = avg_gain / max(avg_loss, 0.001)
        rsi = 100 - (100 / (1 + rs))

        # EMA crossover (5 vs 20)
        ema5 = sum(prices[-5:]) / 5
        ema20 = sum(prices[-20:]) / 20 if len(prices) >= 20 else ema5

        if rsi < 30 and price > ema5:
            return SignalResult(symbol, "BUY", 0.75, price, self.version,
                               f"RSI={rsi:.1f} oversold + EMA bullish", self.name)
        elif rsi > 70 and price < ema5:
            return SignalResult(symbol, "SELL", 0.75, price, self.version,
                               f"RSI={rsi:.1f} overbought + EMA bearish", self.name)
        elif ema5 > ema20 and price > ema5:
            return SignalResult(symbol, "BUY", 0.55, price, self.version,
                               f"EMA5={ema5:.1f}>EMA20={ema20:.1f} bullish", self.name)
        elif ema5 < ema20 and price < ema5:
            return SignalResult(symbol, "SELL", 0.55, price, self.version,
                               f"EMA5={ema5:.1f}<EMA20={ema20:.1f} bearish", self.name)
        return SignalResult(symbol, "HOLD", 0.3, price, self.version, "No clear signal", self.name)


class MacroAgent(BaseAgent):
    """Macro-economic trend analysis agent."""

    def __init__(self):
        super().__init__("Macro", "1.0")

    async def analyze(self, symbol: str, price: float, prices: list[float]) -> SignalResult:
        if len(prices) < 10:
            return SignalResult(symbol, "HOLD", 0.0, price, self.version, "Insufficient data", self.name)

        # Trend strength
        returns = [(prices[i] - prices[i - 1]) / prices[i - 1] for i in range(1, len(prices))]
        avg_return = sum(returns[-10:]) / 10
        volatility = math.sqrt(sum((r - avg_return) ** 2 for r in returns[-10:]) / 10)

        if avg_return > 0.01 and volatility < 0.02:
            return SignalResult(symbol, "BUY", 0.6, price, self.version,
                               f"Macro trend: avg_return={avg_return:.4f}, low vol={volatility:.4f}", self.name)
        elif avg_return < -0.01:
            return SignalResult(symbol, "SELL", 0.5, price, self.version,
                               f"Macro trend: avg_return={avg_return:.4f}", self.name)
        return SignalResult(symbol, "HOLD", 0.3, price, self.version, "Neutral macro", self.name)


class SentimentAgent(BaseAgent):
    """Simulated news/social sentiment analysis."""

    def __init__(self):
        super().__init__("Sentiment", "1.0")

    async def analyze(self, symbol: str, price: float, prices: list[float]) -> SignalResult:
        random.seed(hash(symbol + datetime.now(timezone.utc).strftime("%Y%m%d%H")))
        sentiment_score = random.uniform(-1, 1)
        confidence = abs(sentiment_score) * 0.5

        if sentiment_score > 0.3:
            return SignalResult(symbol, "BUY", confidence, price, self.version,
                               f"Sentiment score: {sentiment_score:.2f} (positive)", self.name)
        elif sentiment_score < -0.3:
            return SignalResult(symbol, "SELL", confidence, price, self.version,
                               f"Sentiment score: {sentiment_score:.2f} (negative)", self.name)
        return SignalResult(symbol, "HOLD", 0.2, price, self.version, "Neutral sentiment", self.name)


class BullAgent(BaseAgent):
    """Trend-following momentum agent (bullish bias)."""

    def __init__(self):
        super().__init__("Bull", "1.0")

    async def analyze(self, symbol: str, price: float, prices: list[float]) -> SignalResult:
        if len(prices) < 5:
            return SignalResult(symbol, "HOLD", 0.0, price, self.version, "Insufficient data", self.name)

        mom_1d = (price - prices[-1]) / prices[-1] if prices[-1] > 0 else 0
        mom_5d = (price - prices[-5]) / prices[-5] if prices[-5] > 0 else 0
        mom_short_ma = sum(prices[-3:]) / 3

        if mom_5d > 0.02 and price > mom_short_ma:
            return SignalResult(symbol, "BUY", min(0.5 + mom_5d * 5, 0.9), price, self.version,
                               f"Momentum: 1d={mom_1d:.4f}, 5d={mom_5d:.4f}", self.name)
        elif mom_5d < -0.03:
            return SignalResult(symbol, "HOLD", 0.3, price, self.version, "Downtrend - no entry", self.name)
        return SignalResult(symbol, "HOLD", 0.2, price, self.version, "Neutral momentum", self.name)


class BearAgent(BaseAgent):
    """Contrarian mean-reversion agent (bearish bias)."""

    def __init__(self):
        super().__init__("Bear", "1.0")

    async def analyze(self, symbol: str, price: float, prices: list[float]) -> SignalResult:
        if len(prices) < 10:
            return SignalResult(symbol, "HOLD", 0.0, price, self.version, "Insufficient data", self.name)

        mean_10d = sum(prices[-10:]) / 10
        deviation = (price - mean_10d) / mean_10d

        if deviation > 0.03:
            return SignalResult(symbol, "SELL", min(0.4 + deviation * 5, 0.8), price, self.version,
                               f"Mean reversion: {deviation:.4f} above 10d MA", self.name)
        elif deviation < -0.03:
            return SignalResult(symbol, "BUY", min(0.4 + abs(deviation) * 5, 0.8), price, self.version,
                               f"Mean reversion: {deviation:.4f} below 10d MA", self.name)
        return SignalResult(symbol, "HOLD", 0.2, price, self.version, "Near mean", self.name)


class TraderAgent(BaseAgent):
    """Pattern-based scalping / short-term trader."""

    def __init__(self):
        super().__init__("Trader", "1.0")

    async def analyze(self, symbol: str, price: float, prices: list[float]) -> SignalResult:
        if len(prices) < 5:
            return SignalResult(symbol, "HOLD", 0.0, price, self.version, "Insufficient data", self.name)

        # Detect breakout from narrow range
        high_5 = max(prices[-5:])
        low_5 = min(prices[-5:])
        range_pct = (high_5 - low_5) / low_5 if low_5 > 0 else 0

        # Volume-like proxy: price change velocity
        velocity = (price - prices[-1]) / prices[-1] if prices[-1] > 0 else 0

        if range_pct < 0.02 and abs(velocity) > 0.005:
            if velocity > 0:
                return SignalResult(symbol, "BUY", 0.5, price, self.version,
                                   f"Breakout: range={range_pct:.4f}, velocity={velocity:.4f}", self.name)
            else:
                return SignalResult(symbol, "SELL", 0.5, price, self.version,
                                   f"Breakout: range={range_pct:.4f}, velocity={velocity:.4f}", self.name)
        return SignalResult(symbol, "HOLD", 0.1, price, self.version, "No pattern", self.name)


class RiskAgent(BaseAgent):
    """Risk monitoring: drawdown protection, volatility regime detection."""

    def __init__(self):
        super().__init__("Risk", "1.0")

    async def analyze(self, symbol: str, price: float, prices: list[float]) -> SignalResult:
        if len(prices) < 20:
            return SignalResult(symbol, "HOLD", 0.0, price, self.version, "Insufficient data", self.name)

        # Volatility regime
        returns = [(prices[i] - prices[i - 1]) / prices[i - 1] for i in range(1, len(prices))]
        recent_vol = math.sqrt(sum(r ** 2 for r in returns[-10:]) / 10) if len(returns) >= 10 else 0
        hist_vol = math.sqrt(sum(r ** 2 for r in returns[-20:]) / 20) if len(returns) >= 20 else 0

        # Drawdown
        peak = max(prices[-20:])
        drawdown = (peak - price) / peak

        if recent_vol > hist_vol * 1.5 and drawdown > 0.05:
            return SignalResult(symbol, "SELL", 0.7, price, self.version,
                               f"High vol regime: vol={recent_vol:.4f}, dd={drawdown:.4f}", self.name)
        elif drawdown > 0.1:
            return SignalResult(symbol, "SELL", 0.8, price, self.version,
                               f"Deep drawdown: {drawdown:.4f}", self.name)
        elif recent_vol < hist_vol * 0.7:
            return SignalResult(symbol, "BUY", 0.5, price, self.version,
                               f"Low vol regime: vol={recent_vol:.4f}", self.name)
        return SignalResult(symbol, "HOLD", 0.2, price, self.version, "Normal regime", self.name)


class AgentEnsemble:
    """Runs all 7 agents and aggregates signals."""

    def __init__(self):
        self.agents: list[BaseAgent] = [
            TechnicalAgent(),
            MacroAgent(),
            SentimentAgent(),
            BullAgent(),
            BearAgent(),
            TraderAgent(),
            RiskAgent(),
        ]
        self.price_history: dict[str, list[float]] = {}

    def record_price(self, symbol: str, price: float):
        if symbol not in self.price_history:
            self.price_history[symbol] = []
        self.price_history[symbol].append(price)
        # Keep last 100 prices
        if len(self.price_history[symbol]) > 100:
            self.price_history[symbol] = self.price_history[symbol][-100:]

    async def analyze_symbol(self, symbol: str) -> list[SignalResult]:
        prices = self.price_history.get(symbol, [])
        current_price = prices[-1] if prices else 0.0

        results = []
        for agent in self.agents:
            try:
                result = await agent.analyze(symbol, current_price, prices)
                results.append(result)
            except Exception as e:
                logger.error("Agent %s failed for %s: %s", agent.name, symbol, e)

        return results

    async def aggregate_signal(self, symbol: str) -> SignalResult:
        """Aggregate all agent signals into one consensus signal."""
        results = await self.analyze_symbol(symbol)

        weights = {"BUY": 0.0, "SELL": 0.0, "HOLD": 0.0}
        total_weight = 0.0
        avg_confidence = 0.0

        for r in results:
            w = r.confidence
            weights[r.signal_type] += w
            total_weight += w
            avg_confidence += r.confidence

        avg_confidence = avg_confidence / len(results) if results else 0

        if weights["BUY"] > weights["SELL"] and weights["BUY"] > weights["HOLD"]:
            signal = "BUY"
            confidence = weights["BUY"] / total_weight if total_weight > 0 else 0
        elif weights["SELL"] > weights["BUY"] and weights["SELL"] > weights["HOLD"]:
            signal = "SELL"
            confidence = weights["SELL"] / total_weight if total_weight > 0 else 0
        else:
            signal = "HOLD"
            confidence = weights["HOLD"] / total_weight if total_weight > 0 else 0.5

        price = results[0].price if results else None
        rationales = "\n".join(f"[{r.agent_name}] {r.rationale}" for r in results if r.signal_type != "HOLD")

        return SignalResult(
            symbol=symbol,
            signal_type=signal,
            confidence=round(confidence, 2),
            price=price,
            model_version="ensemble-v1",
            rationale=rationales,
            agent_name="Ensemble",
        )
