import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_delivery():
    payload = {
        "point_depart": "48.8530,2.3498",
        "point_arrivee": "48.8600,2.3420",
        "taille": "L"
    }
    resp = client.post("/delivery/create", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] is not None
    assert data["point_depart"] == "48.8530,2.3498"
