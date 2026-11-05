import pytest
from fastapi.testclient import TestClient
from server import app

client = TestClient(app)

def test_readiness_endpoint():
    res = client.get("/ready")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ready"
    assert "database" in data

def test_auth_login_success():
    res = client.post("/api/v1/auth/login", json={
        "username": "admin",
        "password": "SentinelAdmin2026!"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "authenticated"
    assert data["role"] == "admin"
    assert "token" in data

def test_auth_login_failure():
    res = client.post("/api/v1/auth/login", json={
        "username": "admin",
        "password": "WrongPassword123"
    })
    assert res.status_code == 401

def test_edge_device_lifecycle():
    # 1. Register Edge Device
    reg_res = client.post("/api/v1/edge/register", json={
        "device_id": "dell-test-unit",
        "device_name": "Dell Latitude Test Unit",
        "token": "test_token_123",
        "camera_source": "Integrated Webcam"
    })
    assert reg_res.status_code == 200

    # 2. Send Heartbeat
    hb_res = client.post("/api/v1/edge/heartbeat", json={
        "device_id": "dell-test-unit",
        "token": "test_token_123",
        "cpu_percent": 45.2,
        "memory_mb": 380.0,
        "status": "ONLINE",
        "camera_source": "Integrated Webcam",
        "active_pipeline": True
    })
    assert hb_res.status_code == 200
    assert hb_res.json()["status"] == "heartbeat_acknowledged"

    # 3. Ingest Telemetry
    telem_res = client.post("/api/v1/edge/telemetry", json={
        "device_id": "dell-test-unit",
        "camera_id": "cam-01",
        "detected_count": 4,
        "active_tracks": 4,
        "tripwire_occupancy": 12,
        "entries": 15,
        "exits": 3,
        "activity_class": "Moderate Activity",
        "confidence": 0.88,
        "blur_score": 110.5,
        "brightness": 85.0,
        "is_reliable": True,
        "fps": 8.5,
        "inference_latency_ms": 115.0,
        "cpu_percent": 50.0,
        "memory_mb": 395.0
    })
    assert telem_res.status_code == 200
    assert telem_res.json()["status"] == "telemetry_ingested"

    # 4. Ingest Alert
    alert_res = client.post("/api/v1/edge/alerts", json={
        "alert_id": "alt-test-01",
        "device_id": "dell-test-unit",
        "alert_type": "high_occupancy",
        "severity": "high",
        "title": "High Density Test",
        "description": "Occupancy exceeded 10 in Zone A"
    })
    assert alert_res.status_code == 200

    # 5. Check Cloud Edge Status
    status_res = client.get("/api/v1/edge/status")
    assert status_res.status_code == 200
    devices = status_res.json()["devices"]
    found = any(d["device_id"] == "dell-test-unit" for d in devices)
    assert found is True
