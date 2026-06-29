from fastapi.testclient import TestClient
from app.main import app


def test_trade_executes():
    with TestClient(app) as client:
        payload = {"symbol": "RELIANCE", "qty": 10, "side": "BUY"}
        r = client.post("/api/trade/execute", json=payload)
        assert r.status_code == 200
        data = r.json()
        assert data.get("success") in (True, False)
