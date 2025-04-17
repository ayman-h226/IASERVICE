import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_update_pricing():
    payload = {
        "id_livraison": 1,
        "accepte": True
    }
    resp = client.post("/pricing/update", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "updated"
