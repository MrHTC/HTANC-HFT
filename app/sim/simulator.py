from typing import Dict, Any
import random

class PaperSimulator:
    def __init__(self, slippage=0.0005, fee=0.0003):
        self.slippage = slippage
        self.fee = fee

    async def execute(self, order: Dict[str, Any]) -> Dict[str, Any]:
        qty = order.get("qty", 0)
        price = order.get("price", 100.0)
        executed_price = price * (1 + random.uniform(-self.slippage, self.slippage))
        executed_qty = qty
        cost = executed_price * executed_qty * (1 + self.fee)
        return {
            "status": "filled",
            "price": executed_price,
            "qty": executed_qty,
            "cost": cost,
        }
