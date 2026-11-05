# Hardware and System Profile

**System Verification Date:** November 5, 2026  
**Platform Verification Script:** `evidence/phase_01/hardware_discovery.json` and `scripts/doctor.ps1`

## 1. Physical Hardware Specifications

| Component | Verified Specification |
| :--- | :--- |
| **System Manufacturer** | Dell Inc. |
| **System Model** | Latitude 3420 |
| **Processor (CPU)** | 11th Gen Intel(R) Core(TM) i5-1145G7 @ 2.60GHz |
| **Physical Cores** | 4 |
| **Logical Processors** | 8 |
| **Max Clock Speed** | 2.60 GHz (1498 MHz base clock state recorded) |
| **Total Physical RAM** | 7.74 GB (8,311,480,320 bytes) |
| **Graphics Adapter (GPU)** | Intel(R) Iris(R) Xe Graphics (Integrated) |
| **Dedicated GPU RAM** | 2048 MB dynamically shared |
| **NVIDIA / CUDA Support** | None (CPU & Intel iGPU only) |
| **Integrated Camera** | Integrated Webcam (`USB\VID_0C45&PID_6738&MI_00\6&517D4FA&0&0000`, Status: OK) |
| **Disk Storage (Drive C:)** | 56.68 GB free / 180.29 GB used |

## 2. Operating System and Execution Environment

| Environment Parameter | Verified Value |
| :--- | :--- |
| **Operating System** | Microsoft Windows 11 Pro (64-bit) |
| **OS Build** | 10.0.26100 (Build 26100) |
| **Host Python Version** | Python 3.11.9 (64-bit) |
| **Package Manager (pip)** | pip 26.1.1 |
| **Power Scheme** | Balanced (`381b4222-f694-41f0-9685-ff5bb260df2e`) |

## 3. Engineering Implications for SENTINEL AI

1. **Strict CPU-First Inference Baseline**: The target device does not have an NVIDIA discrete GPU. All deep learning and computer vision pipelines must run with sub-second latency on the Intel Core i5-1145G7 CPU.
2. **Intel Iris Xe Hardware Acceleration**: OpenVINO and ONNX Runtime CPU execution providers are viable options to accelerate inference without requiring external hardware.
3. **RAM Budgeting**: With 7.74 GB total RAM, the runtime footprint of the vision pipeline, FastAPI, Streamlit, and background worker must remain strictly under 1.5 GB to prevent memory pressure or swapping.
4. **Camera Ingestion**: The integrated camera uses Windows DSHOW/MSMF drivers. Dedicated frame-dropping rings must be used to ensure the capture thread never lags behind real-time display.
