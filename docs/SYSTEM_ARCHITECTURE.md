# SENTINEL AI — System Architecture Specification

**Version:** 2.0.0 (Production-Oriented Edge Architecture)  
**Target Hardware:** Dell Latitude 3420 | Intel Core i5-1145G7 (4 Cores / 8 Threads @ 2.60GHz) | 7.74 GB RAM | Intel Iris Xe Graphics  
**Platform:** Microsoft Windows 11 Pro  

---

## 1. Architectural Philosophy

SENTINEL AI is designed as a **decoupled, CPU-efficient, privacy-conscious indoor crowd-monitoring and occupancy-intelligence platform**. Rather than monolithic synchronous processing or heavy cloud dependencies, SENTINEL AI employs an edge-first pipeline with clear component boundaries:

1. **Strict CPU-First Operation:** Optimized for commodity enterprise and educational laptops without requiring discrete NVIDIA GPUs or CUDA runtime.
2. **Privacy by Design:** Zero biometric facial recognition, zero identity persistence, temporary ephemeral tracking IDs only, and no raw video retention.
3. **Decoupled Edge Worker & API:** Ingestion and computer vision run in an isolated background thread with a non-blocking ring-buffer, preventing UI freezes and blocking I/O.
4. **Reliability & Uncertainty Awareness:** Image quality metrics (Laplacian blur variance, mean brightness) gate occupancy outputs; ambiguous detections trigger explicit human verification flags rather than false certainty.

---

## 2. End-to-End Processing Pipeline

```
[Laptop Webcam (DirectShow) / Video Feed]
                     │
                     ▼
         [ResilientVideoStream] ───────── Drops stale frames to eliminate latency
                     │
                     ▼
         [ImageQualityAssessor] ───────── Computes Laplacian variance & luminance
                     │                    Flags blur / under-exposure / corruption
                     ▼
          [Person Detection Engine]
             ├── SSDLite320-MobileNetV3 (Modern DL Person Detector, COCO Person)
             └── Haar Cascades MultiScale (Empirical Baseline: Frontal+Profile+UpperBody)
                     │
                     ▼
          [RealtimeTracker (IoU)] ─────── Ephemeral Track IDs, velocity, trajectory
                     │
                     ▼
         [Spatial & Flow Modules]
             ├── [TripwireLine] ───────── Bidirectional entry/exit crossing detection
             └── [ZoneManager]  ───────── Polygon ROIs (Classrooms, Corridors, Capacity)
                     │
                     ▼
        [Activity Intelligence] ──────── Kinematic features (flux, velocity variance)
                     │                   Probabilistic Softmax & uncertainty floor
                     ▼
           [Alert Rule Engine] ────────── Cooldown-deduplicated anomaly notifications
                     │
         ┌───────────┴───────────┐
         ▼                       ▼
 [DatabaseManager]       [FastAPI Backend / Streamlit Dashboard]
 (SQLite WAL Mode)       (REST Endpoints, MJPEG Stream, Premium Dark UI)
```

---

## 3. Core Subsystems

### 3.1 Video Ingestion Subsystem (`sentinel.capture`)
* Utilizes Windows DirectShow (`cv2.CAP_DSHOW`) with buffer size 1 to prevent Windows capture lag.
* Thread-isolated capture loop updates `latest_frame` atomically under a mutex lock.
* Provides automatic fallback to synthetic high-contrast test feeds during headless testing or when physical devices are locked.

### 3.2 Visual Reliability Subsystem (`sentinel.quality`)
* **Blur Quantification:** Variance of Laplacian $\sigma^2 = \text{Var}(\nabla^2 I)$. Threshold: $\sigma^2 < 60.0$ triggers blur alert.
* **Photometric Quantification:** Mean luminance $\mu = \frac{1}{HW}\sum I(x, y)$. Thresholds: $\mu < 30$ (low light) or $\mu > 230$ (overexposed).
* Generates human review recommendations when image quality drops.

### 3.3 Person Detection Subsystem (`sentinel.detection`)
* **Proposed Modern Detector:** `SSDLite320_MobileNet_V3_Large` pre-trained on COCO (13.4 MB). Specifically tuned for mobile/edge CPU inference, detecting full pedestrian bodies rather than faces.
* **Empirical Baseline:** OpenCV Haar Cascade fusion (`haarcascade_frontalface_default.xml`, `haarcascade_profileface.xml`, `haarcascade_upperbody.xml`) with OpenCV NMS. Preserved for comparative ablation experiments.

### 3.4 Multi-Object Tracking Subsystem (`sentinel.tracking`)
* Realtime greedy IoU association with trajectory history (30-frame window).
* Velocity smoothing: $\vec{v}_t = 0.7\vec{v}_{t-1} + 0.3(\vec{c}_t - \vec{c}_{t-1})$.
* Track lifecycle: Minimum 2 hits before confirmation; max 15 frames of grace period before track expiration.
* Zero identity retention: Track IDs are positive integers reset upon monitoring restart.

### 3.5 Occupancy & Spatial Subsystem (`sentinel.occupancy`)
* **Tripwire Crossing:** Analyzes vertical displacement across line $y = y_{\text{fraction}} \times H$. Downward displacement incrementing entries; upward displacement incrementing exits.
* **Occupancy Formulation:**
  $$\text{Estimated Occupancy} = \text{Initial} + \text{Entries} - \text{Exits} + \Delta_{\text{manual}}$$
* **Monitoring Zones:** Arbitrary polygon point-in-polygon tests (`cv2.pointPolygonTest`) mapping tracks to defined facilities (Zone A Corridor, Zone B Hall) with density percentage calculation.

### 3.6 Activity Intelligence Subsystem (`sentinel.activity`)
* Computes kinematic activity energy:
  $$E_{\text{kinetic}} = N_{\text{tracks}} \times \left(1.0 + 0.15 \bar{v} + 0.1 \Phi\right)$$
  where $\bar{v}$ is mean velocity and $\Phi$ is movement flux.
* Output classes: "Low Activity", "Moderate Activity", "High Activity" with uncertainty thresholding.

### 3.7 Storage & Persistence Subsystem (`sentinel.storage`)
* Lightweight embedded SQLite engine with Write-Ahead Logging (`PRAGMA journal_mode=WAL;`).
* Tables: `occupancy_telemetry`, `alerts`, `system_health_logs`.
* Aggregated hourly and daily telemetry queries.

---

## 4. Hardware Resource Budgeting

| Resource | Allocated Budget | Measured Runtime (i5-1145G7) | Headroom |
| :--- | :--- | :--- | :--- |
| **CPU Utilization** | $\le 85\%$ | $65\% - 75\%$ | Sufficient |
| **RAM (RSS)** | $\le 1500$ MB | $\sim 391$ MB | $> 1100$ MB free |
| **Inference Latency** | $\le 200$ ms | $110 - 135$ ms | Within target |
| **Pipeline Framerate**| $\ge 5$ FPS | $6.5 - 9.0$ FPS | Interactive |
