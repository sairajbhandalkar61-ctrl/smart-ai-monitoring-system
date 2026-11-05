# SENTINEL AI — Deployment and Operational Guide

---

## 1. Local Windows Execution (Native Dell Latitude 3420)

### 1.1 Prerequisites
* Windows 10/11 Pro (64-bit)
* Python 3.11.x (Installed and on system `PATH`)
* Webcam (Integrated or external USB)
* Minimum 4 GB RAM (8 GB recommended)

### 1.2 Quickstart Setup
Open PowerShell as Administrator or regular user:
```powershell
# 1. Run diagnostic and environment initialization
.\scripts\setup_windows.ps1
```

### 1.3 Running the System
```powershell
# Launch Streamlit Command Center (Default: http://localhost:8501)
.\scripts\run_sentinel.ps1 -Mode dashboard

# Or launch FastAPI REST server (Default: http://127.0.0.1:8000)
.\scripts\run_sentinel.ps1 -Mode api

# Or launch both concurrently
.\scripts\run_sentinel.ps1 -Mode all
```

---

## 2. Environment Configuration (`.env`)

```ini
APP_ENV=development
API_HOST=127.0.0.1
API_PORT=8000
DASHBOARD_PORT=8501

# Hardware Camera Configuration
CAMERA_INDEX=0
CAMERA_BACKEND=DSHOW
FRAME_WIDTH=640
FRAME_HEIGHT=480

# Vision Engine
DETECTOR_TYPE=ssdlite
CONFIDENCE_THRESHOLD=0.40
NMS_IOU_THRESHOLD=0.45

# Privacy
STORE_RAW_VIDEO=false
```

---

## 3. Docker Container Deployment

For headless server or Linux deployments:
```bash
# Build container image
docker build -t sentinel-ai:2.0.0 .

# Run container (Headless API mode)
docker run -d -p 8000:8000 --name sentinel-edge sentinel-ai:2.0.0
```
*Note for Windows Docker users:* Physical webcam access through Windows DirectShow is not supported inside standard WSL2/Docker containers without USB/IP bridging. Use native Windows execution for physical webcam access.
