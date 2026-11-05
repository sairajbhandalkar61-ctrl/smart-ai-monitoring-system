from fastapi.testclient import TestClient
import pytest
from server import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "pipeline_active" in data

def test_telemetry_endpoint():
    response = client.get("/api/v1/telemetry")
    assert response.status_code == 200
    data = response.json()
    assert "estimated_occupancy" in data
    assert "fps" in data
    assert "active_tracks_count" in data

def test_legacy_stats_endpoint():
    response = client.get("/api/stats")
    assert response.status_code == 200
    data = response.json()
    assert "estimated_occupancy" in data
    assert "model_used" in data
