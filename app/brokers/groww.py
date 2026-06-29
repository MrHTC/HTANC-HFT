from app.brokers.base import BrokerBase

class GrowwBroker(BrokerBase):
    def __init__(self, api_key: str):
        self.api_key = api_key

    async def place_order(self, order):
        return {"status": "simulated", "broker": "groww", "order": order}

    async def cancel_order(self, order_id: str):
        return {"status": "cancelled", "order_id": order_id}
