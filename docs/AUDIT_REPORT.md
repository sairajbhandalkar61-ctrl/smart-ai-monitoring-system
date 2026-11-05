# SENTINEL AI — Comprehensive Technical Audit Report

**Audit Date:** November 5, 2026  
**Auditor:** Automated Senior AI/ML Architecture & QA Suite  
**Scope:** Complete repository inspection (`smart-ai-monitoring-system-main`)

---

## 1. Executive Summary

An exhaustive technical audit of the original repository was conducted across all files, datasets, model weights, API routes, and frontend assets. While the project presents a functional computer-vision prototype combining OpenCV Haar cascades and an interactive UI, critical engineering, data science, and security deficiencies were identified that prevent it from functioning as an authentic research-grade surveillance system in its original state.

Key findings include:
1. **Target Leakage and Degenerate Classifier:** The dataset `data.csv` contains exclusively "Low" class examples (939 "Low", 2 "Low Activity", counts 0–2). The shipped ANN (`dl_model.h5`) has a single output unit with Softmax, meaning it can only ever output 100% confidence for "Low".
2. **Face Counting Labeled as Person Counting:** `detection.py` uses face and upper-body cascades, labeling candidate boxes as "Person #n" without multi-object tracking.
3. **Hardcoded Telemetry and Simulated UI:** The FastAPI `/api/stats` endpoint and web frontend presented static and randomized demo figures (12 faces, 1208 predictions, 120 FPS) as live telemetry.
4. **Hardware Reality:** The host laptop is an Intel Core i5-1145G7 with Intel Iris Xe graphics (no NVIDIA/CUDA GPU). All vision processing must be strictly optimized for CPU execution.

---

## 2. Codebase Component Inventory & Line-by-Line Findings

### 2.1 Computer Vision Module (`detection.py`)
* **Haar Cascades Used:** `haarcascade_frontalface_default.xml`, `haarcascade_profileface.xml`, and `haarcascade_upperbody.xml`.
* **Preprocessing:** Grayscale conversion (`cv2.cvtColor`) and histogram equalization (`cv2.equalizeHist`).
* **Non-Maximum Suppression (NMS):** Calls `cv2.dnn.NMSBoxes` using constant dummy confidence scores (`[0.95, 0.90, 0.85]`), score threshold 0.5, and NMS threshold 0.4.
* **Limitations Identified:**
  * No multi-object tracking: Box index `idx + 1` is assigned as the ID, meaning IDs fluctuate chaotically frame to frame.
  * No frame resizing: Processes raw incoming frame dimensions directly, leading to variable CPU latency.
  * Face detection is not person counting: Inward-facing or occluded pedestrians are completely missed.

### 2.2 Machine Learning & Neural Network Pipeline (`ml_model.py`, `training/`)
* **Data File (`data.csv`):** 941 rows, 3 columns (`time`, `count`, `activity`). Class distribution: 939 `Low`, 2 `Low Activity`. Count values: `0` (626), `1` (306), `2` (9). Max count observed is 2.
* **Processed Data (`training/processed_data.csv`):** Only 3 rows, all labeled `Low` with `hour=18` and `count_diff=0.0`.
* **Model Artifacts (`models/`):**
  * `dl_model.h5`: Keras Sequential with `Dense(16, relu)` -> `Dense(8, relu)` -> `Dense(1, softmax)`. Total parameters: 211.
  * `scaler.pkl`: StandardScaler fitted with mean `[1., 18., 0.]` and scale `[1., 1., 1.]`.
  * `label_encoder.pkl`: Contains a single class: `['Low']`.
  * `crowd_model.pkl`: Scikit-learn RandomForestClassifier trained in `train_model.py`, but completely unreferenced in runtime inference.
* **Critical Flaws Identified:**
  * **Target Leakage:** `training/features.py` defined activity as a deterministic rule: `count >= 5 -> High`, `count >= 2 -> Moderate`, else `Low`. The ANN merely attempts to memorize an if-else statement.
  * **StandardScaler Leakage:** Fitted across the entire dataset before splitting in `train_dl_model.py`.
  * **Out-of-Distribution Temporal Feature:** The model was trained only on hour `18`. When querying during daytime (e.g., hour `10`), the scaled value diverges severely from training data.

### 2.3 Backend API (`server.py`)
* **Framework:** FastAPI with Uvicorn.
* **Security Deficiencies:**
  * Wide-open CORS (`allow_origins=["*"]`, `allow_credentials=True`).
  * No authentication or API token validation.
  * `/api/snapshot` allows arbitrary base64 uploads without size caps, MIME validation, or rate limits.
* **Hardcoded Telemetry:**
  * `/api/stats` returned static numbers: 12 faces, +3 change, 120 FPS, 1208 predictions.
  * Uptime was artificially padded by +1104 seconds.

### 2.4 Streamlit Dashboard (`app.py`)
* **Execution Flow:** Runs a blocking `while True:` loop inside Streamlit with `time.sleep(0.1)`.
* **Silent Fallback Flaw:** If the webcam fails to open, it silently loops a static image (`surveillance_sample.jpg`) while continuing to display live detection boxes and predictions, violating integrity rule R5.

### 2.5 Web Frontend (`static/app.js`, `index.html`)
* **Marketing Claims:** Displayed "120 FPS", "120Hz Pro", and simulated pedestrians with `Math.random()`.
* **Client Fallback:** Implemented a pure if/else threshold check in JavaScript mislabeled in the README as "in-browser neural inference".

---

## 3. Action Plan & Required Transformations

1. **Re-architect Detection & Tracking:** Retain Haar cascade as a labeled legacy baseline; integrate modern lightweight person detector (e.g. YOLO-Nano / MobileNet SSD via ONNX CPU) and real multi-object tracking (ByteTrack / SORT).
2. **Rebuild Activity Intelligence:** Replace the circular count-threshold classification with kinematic track features (velocity, dispersion, acceleration, density).
3. **Refactor Backend to Production Standards:** Implement FastAPI router structure with OAuth2/JWT authentication, Pydantic v2 schemas, SQLite/PostgreSQL persistence, and live MJPEG streaming.
4. **Honest Evaluation & Documentation:** All claims in `README.md` and documentation must be backed by genuine test benchmarks.
