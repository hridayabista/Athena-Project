# control-plane/tests/test_main.py
from fastapi.testclient import TestClient
import pytest

# THIS IS THE UPDATED IMPORT:
from app.main import app

client = TestClient(app)

def test_root():
    r = client.get("/")
    assert r.status_code == 200
    assert "Welcome to the Athena Control Plane" in r.json().get("message", "")

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}

def test_load_model():
    payload = {"model_name": "fraud-detector", "version": "v0.1"}
    r = client.post("/models/load", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data.get("loaded") == "fraud-detector:v0.1"

def test_get_model_not_found():
    r = client.get("/models/nonexistent")
    assert r.status_code == 200
    assert r.json().get("status") == "not_loaded"