from typing import Dict, Any

class BrokerBase:
    async def place_order(self, order: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError()

    async def cancel_order(self, order_id: str) -> Dict[str, Any]:
        raise NotImplementedError()
