# control_plane/tests/test_main.py

from fastapi.testclient import TestClient
import pytest

# THIS IS THE UPDATED IMPORT:
from control_plane.app.main import app

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
    # This test now ensures the database persistence and ModelOut response schema are correct.
    payload = {"model_name": "fraud-detector", "version": "v0.1"}
    r = client.post("/models/load", json=payload)
    assert r.status_code == 200
    data = r.json()
    
    # NEW ASSERTIONS: The endpoint returns the full ModelOut object, not a simple "loaded" message.
    assert data.get("name") == "fraud-detector"
    assert data.get("version") == "v0.1"
    assert data.get("status") == "loaded" # Checks the status field
    assert "id" in data # Ensures a primary key ID was assigned by the DB
    
def test_get_model_not_found():
    r = client.get("/models/nonexistent")
    assert r.status_code == 200
    
    # NOTE: The app now returns a dictionary, which includes the 'status' field correctly.
    assert r.json().get("status") == "not_loaded"