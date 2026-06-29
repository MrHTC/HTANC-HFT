from app.sim.simulator import PaperSimulator
from app.risk.engine import RiskEngine

class Orchestrator:
    def __init__(self):
        self.sim = PaperSimulator()
        self.risk = RiskEngine()

    async def process_order(self, portfolio, order):
        check = self.risk.check_order(portfolio, order)
        if not check.get("allowed"):
            return {"status": "rejected", "reason": check.get("reason")}
        exec_result = await self.sim.execute(order)
        return {"status": "executed", "exec": exec_result}
