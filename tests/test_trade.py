from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_trade_executes():
    payload = {"symbol": "TEST", "qty": 1, "price": 100}
    r = client.post("/trade", json=payload)
    assert r.status_code == 200
    assert r.json().get("status") == "executed"
