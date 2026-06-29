from typing import Dict, Any

class RiskEngine:
    def __init__(self, max_drawdown_pct=6.0, intraday_loss_limit_pct=1.5):
        self.max_drawdown_pct = max_drawdown_pct
        self.intraday_loss_limit_pct = intraday_loss_limit_pct

    def check_order(self, portfolio: Dict[str, Any], order: Dict[str, Any]) -> Dict[str, Any]:
        # Very small deterministic checks: notional limit, simple F&O placeholder
        notional = order.get("qty", 0) * order.get("price", 0)
        if notional <= 0:
            return {"allowed": False, "reason": "invalid notional"}
        if portfolio.get("cash", 0) < notional * 0.1:
            return {"allowed": False, "reason": "insufficient margin (min 10% required)"}
        return {"allowed": True}
