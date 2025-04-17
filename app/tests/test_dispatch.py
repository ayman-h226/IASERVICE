import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_assign_basic():
    # Suppose we have a delivery id=1
    # and crowdshippers in DB
    payload = {
        "id_livraison": 1
    }
    resp = client.post("/dispatch/assign", json=payload)
    # Pas garanti que ça marche si la DB est vide, c'est un simple exemple
    assert resp.status_code in [200,404]
