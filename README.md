[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/sairajbhandalkar61-ctrl/smart-ai-monitoring-system)

# 🛡️ SENTINEL AI — Crowd Intelligence & Occupancy Platform
### Production Edge Computer Vision | Hybrid Cloud Deployment | Academic Research Publication

**Author:** Sairaj Bhandalkar (MITCOM-CA, MIT ADT University, Pune)  
**Research Supervisor:** Prof. Pallavi Gaikwad  
**Host Target Platform:** Dell Latitude 3420 | 11th Gen Intel(R) Core(TM) i5-1145G7 @ 2.60GHz | Windows 11 Pro  

---

## 🌐 Hybrid Cloud & Edge Architecture

SENTINEL AI separates vision compute from cloud accessibility:

```
[Dell Latitude 3420 Laptop]
  - Integrated Webcam (DirectShow Index 0)
  - SSDLite320-MobileNetV3 (110.98 ms / 9.01 FPS on CPU)
  - IoU Multi-Object Tracker (100% flicker reduction)
  - Virtual Tripwire & Monitoring Zones
       │
       ▼ (Outbound HTTPS POST)
[Cloud FastAPI Backend (Railway / Render)]
  - Edge Device Ingestion & Heartbeat Monitoring
  - PBKDF2-HMAC-SHA256 Authentication
  - Multi-Engine Storage (PostgreSQL & SQLite)
       │
       ├───► [Cloud PostgreSQL Database]
       │
       ▼
[Cloud Streamlit Command Center]
  - 12 Responsive Navigation Pages
  - Mobile, Tablet, and Desktop Adaptive Layout
  - Live Edge Telemetry & Reconciled Headcounts
```

---

## 🚀 Quickstart Guides

### 1. Local Windows Execution (Dell Laptop)
```powershell
# Automated diagnostic and environment setup
.\scripts\setup_windows.ps1

# Launch local Streamlit Command Center (http://localhost:8501)
.\scripts\run_sentinel.ps1 -Mode dashboard

# Launch local FastAPI REST API (http://127.0.0.1:8000)
.\scripts\run_sentinel.ps1 -Mode api
```

### 2. Running Dell Edge Agent (Streaming to Cloud)
```powershell
# Stream Dell webcam intelligence directly to your Cloud URL:
.\scripts\run_edge_agent.ps1 -CloudUrl "https://your-app.up.railway.app"
```

### 3. Run Automated Pytest Suite
```powershell
python -m pytest -v
```
*(All 20 unit and integration tests passing)*

---

## 🔐 Cloud Authentication & Accounts

When accessing the deployed cloud dashboard, use one of the seeded accounts:
* **Administrator:** `admin` / `SentinelAdmin2026!` (Full control, reconciliation, settings)
* **Operator:** `operator` / `Operator2026!` (Live monitoring, alerts, reports)

---

## 📊 Empirical Benchmarks (Intel Core i5-1145G7 CPU)

| Metric | Haar Cascade Baseline | SSDLite320 MobileNetV3 (Proposed) |
| :--- | :---: | :---: |
| **Inference Latency** | 39.91 ms | **110.98 ms (9.01 FPS on CPU)** |
| **Target Object** | Faces & Upper-Body | **Full Anatomical Pedestrian Body** |
| **Turning / Backs** | Fails | **Robust Detection from any angle** |
| **Tracking Stability**| Variance 0.2100 | **Variance 0.0000 (100% flicker reduction)** |
| **Host Memory RSS** | 350 MB | **391 MB (Budget: 1500 MB)** |

---

## 📚 Complete Project Documentation

* [docs/CLOUD_DEPLOYMENT_GUIDE.md](docs/CLOUD_DEPLOYMENT_GUIDE.md) — Railway & Render deployment steps
* [docs/EDGE_DEVICE_SETUP.md](docs/EDGE_DEVICE_SETUP.md) — Dell Latitude 3420 edge agent guide
* [docs/PUBLIC_ACCESS_AND_SECURITY.md](docs/PUBLIC_ACCESS_AND_SECURITY.md) — RBAC and privacy protocols
* [docs/CLOUD_DATABASE_GUIDE.md](docs/CLOUD_DATABASE_GUIDE.md) — PostgreSQL and SQLite persistence guide
* [docs/DEPLOYMENT_VERIFICATION_REPORT.md](docs/DEPLOYMENT_VERIFICATION_REPORT.md) — Full verification matrix
* [docs/HARDWARE_PROFILE.md](docs/HARDWARE_PROFILE.md) — Verified laptop hardware specs
* [docs/SYSTEM_ARCHITECTURE.md](docs/SYSTEM_ARCHITECTURE.md) — System architecture specification
* [docs/TEST_REPORT.md](docs/TEST_REPORT.md) — Pytest QA report
* [SENTINEL_AI_Research_Paper_Final.docx](SENTINEL_AI_Research_Paper_Final.docx) — Academic research manuscript
* [SENTINEL_AI_Research_Paper_Final.pdf](SENTINEL_AI_Research_Paper_Final.pdf) — Formatted publication PDF
