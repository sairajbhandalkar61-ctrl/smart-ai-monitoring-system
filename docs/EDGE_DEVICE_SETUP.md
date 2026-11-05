# SENTINEL AI — Dell Latitude 3420 Edge Node Setup Guide

**Target Hardware:** Dell Latitude 3420 Laptop  
**Operating System:** Windows 11 Pro (64-bit)  
**Processor:** 11th Gen Intel(R) Core(TM) i5-1145G7 @ 2.60GHz  
**Camera:** Integrated 720p HD Webcam via DirectShow (`cv2.CAP_DSHOW`)  

---

## 1. Edge Agent Concept

The Dell laptop operates as an **autonomous edge compute sensor**. It ingests high-resolution video locally, executes deep learning person detection, tracks individuals, computes tripwire crossings, and pushes structured metadata out to the Cloud.

### Key Security & Network Features:
* **Zero Inbound Ports:** The laptop requires zero open firewall ports and no router port forwarding. It operates entirely on outbound HTTPS POST requests to the Cloud API.
* **Zero Video Transmission:** Raw video never leaves the Dell laptop's RAM. Only numerical counts, bounding box coordinates, and telemetry records are transmitted.
* **Offline Resilient Buffer:** If campus WiFi drops, telemetry records accumulate in a FIFO queue (up to 500 records) and flush automatically upon reconnection.

---

## 2. Installation & Verification

### Step 1: Run Edge Installer
Open PowerShell in the project directory:
```powershell
.\scripts\install_edge_agent.ps1
```
This script checks the Intel CPU, tests Python dependencies, and confirms DirectShow camera access.

### Step 2: Start the Edge Agent
To stream telemetry to your local backend (testing):
```powershell
.\scripts\run_edge_agent.ps1 -CloudUrl "http://127.0.0.1:8000"
```
To stream telemetry to your live Cloud deployment (Railway / Render):
```powershell
.\scripts\run_edge_agent.ps1 -CloudUrl "https://your-app.up.railway.app"
```

### Step 3: Stop Edge Agent
Press `Ctrl+C` in the terminal, or run:
```powershell
.\scripts\stop_edge_agent.ps1
```
