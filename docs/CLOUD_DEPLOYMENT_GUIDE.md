# SENTINEL AI — Cloud Production Deployment Guide

**Target Deployment Platforms:** Railway (Primary) | Render (Alternative) | Docker VPS  
**Architecture:** Hybrid Cloud Ingestion & Analytics + Windows Edge Computer Vision  

---

## 1. Architectural Model Overview

SENTINEL AI separates responsibilities to ensure both high-performance real-time vision on the physical laptop and ubiquitous public access to the dashboard from any smartphone, tablet, or desktop:

```
[Dell Latitude 3420 Edge Node]
  - Integrated Webcam (DirectShow Index 0)
  - SSDLite320-MobileNetV3 (CPU Inference)
  - Real-time IoU Multi-Object Tracking
  - Virtual Tripwire & Zones
  - Local SQLite Cache / Offline Queue
       │
       ▼ (Secure Outbound HTTPS POST)
[Cloud FastAPI Backend (Railway / Render)]
  - Device Registration & Heartbeat Monitor
  - High-Throughput Telemetry Ingestion
  - Authentication (PBKDF2-HMAC-SHA256)
  - REST & Readiness Endpoints (/ready, /health)
       │
       ├───► [Cloud PostgreSQL Database (Persistent Storage)]
       │
       ▼
[Cloud Streamlit Command Center (Port 8501 / $PORT)]
  - Responsive UI (Mobile / Tablet / Desktop)
  - Live Edge Status & Macro Telemetry
  - Role-Based Access (Admin / Operator / Viewer)
```

---

## 2. Deploying to Railway (Recommended)

Railway provides native GitHub continuous deployment, automatic container builds via Dockerfile, managed PostgreSQL, and free custom/public `.up.railway.app` HTTPS domains.

### Step 2.1: Push Repository to GitHub
1. Create a repository on your GitHub account (e.g., `sentinel-ai`).
2. Push your local repository:
```powershell
git remote add origin https://github.com/<your-username>/sentinel-ai.git
git branch -M main
git push -u origin main
```

### Step 2.2: Create Project on Railway
1. Log in to [Railway](https://railway.app).
2. Click **+ New Project** -> **Deploy from GitHub repo**.
3. Select your `sentinel-ai` repository.

### Step 2.3: Add Managed PostgreSQL Database
1. Within your Railway project canvas, click **+ Create** -> **Database** -> **Add PostgreSQL**.
2. Railway automatically provisions a high-availability PostgreSQL instance and injects the `DATABASE_URL` environment variable into your project.

### Step 2.4: Configure Environment Variables
In the **Variables** tab of your Railway web service, verify:
* `APP_ENV`: `production`
* `IS_CLOUD`: `true`
* `PORT`: `8501`
* `DATABASE_URL`: `${{Postgres.DATABASE_URL}}` (Injected automatically by Railway)
* `SECRET_KEY`: `sentinel_prod_secure_secret_key_2026`

### Step 2.5: Generate Public Domain
1. In your Railway service settings, navigate to the **Networking** section.
2. Click **Generate Domain**.
3. Railway will assign an official public HTTPS link, such as:
   `https://sentinel-ai-production.up.railway.app`

---

## 3. Alternative: Deploying to Render via Blueprint

If using Render:
1. Log in to [Render Dashboard](https://dashboard.render.com).
2. Click **New +** -> **Blueprint**.
3. Connect your GitHub repository.
4. Render will parse `render.yaml`, automatically spinning up:
   * Web Service (`sentinel-ai-cloud`)
   * Managed PostgreSQL Database (`sentinel-postgres`)
5. Render assigns a public HTTPS address: `https://sentinel-ai-cloud.onrender.com`.

---

## 4. Connecting the Dell Laptop Edge Agent to Cloud

Once your public domain is live (e.g. `https://sentinel-ai-production.up.railway.app`):
1. Open PowerShell on your Dell Latitude 3420.
2. Run the edge agent launcher pointing to your live cloud URL:
```powershell
.\scripts\run_edge_agent.ps1 -CloudUrl "https://sentinel-ai-production.up.railway.app"
```
3. The Dell laptop immediately registers with the cloud, streams real-time occupancy updates, and sends continuous heartbeats.
4. Open the public link on your phone or tablet to view live occupancy, active tracks, and safety alerts!
