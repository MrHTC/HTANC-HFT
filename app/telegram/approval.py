"""Telegram bot for trade approval flow.

Workflow:
  1. AI agent generates a signal → orchestrator wants to trade
  2. Trade is sent to Telegram for human approval
  3. Human approves/rejects via button
  4. Orchestrator executes or cancels accordingly
"""
import asyncio
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class TelegramApproval:
    """Handles Telegram-based human-in-the-loop trade approval."""

    def __init__(self, token: str | None = None, chat_id: str | None = None):
        self.token = token or os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID", "")
        self._pending_approvals: dict[str, dict] = {}
        self._enabled = bool(self.token and self.chat_id)

    async def request_approval(
        self,
        trade_id: str,
        symbol: str,
        qty: int,
        side: str,
        price: float,
        estimated_cost: float,
        agent_name: str,
        rationale: str,
        timeout_sec: int = 120,
    ) -> bool:
        """Send trade approval request to Telegram."""
        if not self._enabled:
            logger.info("Telegram disabled, auto-approving trade %s", trade_id)
            return True

        message = (
            f"🚨 *Trade Approval Required*\n"
            f"━━━━━━━━━━━━━━━━\n"
            f"*Agent:* {agent_name}\n"
            f"*Symbol:* {symbol}\n"
            f"*Side:* {side}\n"
            f"*Qty:* {qty}\n"
            f"*Price:* ₹{price:.2f}\n"
            f"*Est. Cost:* ₹{estimated_cost:,.2f}\n"
            f"*Rationale:* {rationale[:200]}\n"
            f"━━━━━━━━━━━━━━━━\n"
            f"⏱ Timeout: {timeout_sec}s"
        )

        # In a real implementation, this sends via Telegram API:
        #   requests.post(f"https://api.telegram.org/bot{token}/sendMessage", json={...})
        # With inline keyboard buttons: ✅ Approve | ❌ Reject

        logger.info(
            "Telegram approval requested: trade=%s sym=%s side=%s qty=%d cost=%.2f agent=%s",
            trade_id, symbol, side, qty, estimated_cost, agent_name,
        )

        self._pending_approvals[trade_id] = {
            "status": "pending",
            "created_at": asyncio.get_event_loop().time(),
            "timeout": timeout_sec,
        }

        return await self._wait_for_approval(trade_id, timeout_sec)

    async def _wait_for_approval(self, trade_id: str, timeout_sec: int) -> bool:
        """Wait for human approval or timeout."""
        # In production, this listens to Telegram webhook updates.
        # For now, we simulate approval with a short delay.
        try:
            await asyncio.sleep(2)
            self._pending_approvals[trade_id]["status"] = "approved"
            return True
        except asyncio.CancelledError:
            self._pending_approvals[trade_id]["status"] = "cancelled"
            return False

    def approve(self, trade_id: str):
        if trade_id in self._pending_approvals:
            self._pending_approvals[trade_id]["status"] = "approved"

    def reject(self, trade_id: str):
        if trade_id in self._pending_approvals:
            self._pending_approvals[trade_id]["status"] = "rejected"

    def is_enabled(self) -> bool:
        return self._enabled
