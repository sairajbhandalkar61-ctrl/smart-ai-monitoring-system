# SENTINEL AI — API Documentation

**Base URL:** `http://127.0.0.1:8000`  
**API Specification:** OpenAPI 3.1 / Swagger (Interactive documentation at `http://127.0.0.1:8000/docs`)  

---

## 1. System & Health Endpoints

### `GET /health`
Returns system vitality, node status, and pipeline execution state.
* **Response (200 OK):**
```json
{
  "status": "healthy",
  "system": "SENTINEL AI Edge Node",
  "timestamp": 1793903512.4,
  "uptime_seconds": 124.5,
  "pipeline_active": true
}
```

---

## 2. Real-Time Telemetry Endpoints

### `GET /api/v1/telemetry`
Returns instantaneous multi-modal edge metrics including estimated occupancy, tracked pedestrian count, inference framerate, latency, visual quality, and active zone status.
* **Response (200 OK):**
```json
{
  "active": true,
  "camera_source": "Hardware Camera (0) [640x480]",
  "is_synthetic": false,
  "detector_type": "ssdlite",
  "model_name": "SSDLite320-MobileNetV3-CPU",
  "fps": 6.8,
  "inference_latency_ms": 110.5,
  "end_to_end_latency_ms": 138.2,
  "cpu_percent": 68.4,
  "memory_mb": 392.1,
  "raw_detections_count": 2,
  "active_tracks_count": 2,
  "estimated_occupancy": 5,
  "entries": 8,
  "exits": 3,
  "tripwire_y": 240,
  "activity": "Low Activity",
  "activity_confidence": 0.85,
  "activity_uncertain": false,
  "quality_status": "Optimal Quality",
  "quality_reliable": true,
  "blur_score": 98.4,
  "brightness": 64.2,
  "zones": [
    {
      "zone_id": "zone-a",
      "name": "Zone A (Corridor)",
      "polygon": [[0, 0], [288, 0], [288, 480], [0, 480]],
      "capacity": 10,
      "current_count": 1,
      "density_percentage": 10.0,
      "status": "Normal"
    }
  ],
  "recent_alerts": []
}
```

### `GET /api/v1/stream/live`
Streams multipart/x-mixed-replace continuous MJPEG video stream with bounding boxes, trajectory trails, tripwire lines, and HUD overlays.
* **Content-Type:** `multipart/x-mixed-replace; boundary=frame`

---

## 3. Monitoring Control Endpoints

### `POST /api/v1/monitoring/start`
Starts camera acquisition and background vision pipeline.
* **Response:** `{"status": "started", "active": true}`

### `POST /api/v1/monitoring/stop`
Stops background worker and releases hardware camera handles.
* **Response:** `{"status": "stopped", "active": false}`

### `POST /api/v1/monitoring/detector`
Hot-swaps detection engine between modern Deep Learning and baseline Haar cascade.
* **Request:**
```json
{
  "detector": "ssdlite"
}
```
* **Response:**
```json
{
  "status": "updated",
  "detector": "ssdlite",
  "model": "SSDLite320-MobileNetV3-CPU"
}
```

---

## 4. Occupancy Reconciliation & Alerts

### `POST /api/v1/occupancy/reconcile`
Allows facility managers to adjust running tripwire occupancy to correct for tracking drift.
* **Request:**
```json
{
  "correct_occupancy": 12
}
```
* **Response:**
```json
{
  "status": "reconciled",
  "new_estimated_occupancy": 12,
  "manual_offset": 4
}
```

### `GET /api/v1/alerts`
Retrieves incident log with optional severity filtering.
* **Query Parameters:** `limit=20`, `severity=warning|high|critical`

### `POST /api/v1/alerts/{alert_id}/acknowledge`
Acknowledges an alert event.
