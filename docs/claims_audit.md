# Audit of Project Claims vs. Verified Implementation

This audit evaluates every claim made in the original repository's `README.md`, marketing materials, UI badges, and source code against the verified technical implementation.

**Classification:**
* `[VERIFIED]` = Present, functional, and supported by code and tests.
* `[UNVERIFIED]` = Stated or partially coded, but lacks experimental validation or benchmark evidence.
* `[FALSE]` = In contradiction with the actual code, hardcoded, or fabricated.

---

## 1. Computer Vision & Detection Claims

| Stated Claim | Location | Audit Finding | Status | Required Remedy |
| :--- | :--- | :--- | :--- | :--- |
| "Real-time webcam-based people detection" | README.md, app.py | Uses Haar cascades (frontal face, profile face, upper body). Only detects faces/upper bodies, not full persons. | `[UNVERIFIED]` | Relabel as "Face and Upper-Body Baseline Detection"; integrate modern person detector for actual people counting. |
| "Non-Maximum Suppression (NMS) to eliminate duplicate bounding boxes" | README.md, detection.py | `cv2.dnn.NMSBoxes` is called with hardcoded scores (0.95, 0.90, 0.85). Effective for geometric overlap filtering, but scores are dummy constants. | `[VERIFIED]` | Retain NMS implementation; document that scores are heuristic cascade tier weights. |
| "Person #n Tracking" | detection.py, app.js | Bounding boxes are enumerated by loop index `idx + 1`. No tracking algorithm (Kalman, SORT, ByteTrack) exists; IDs change every frame. | `[FALSE]` | Implement genuine multi-object tracker (ByteTrack/SORT) with consistent track IDs. |

---

## 2. Deep Learning & Machine Learning Claims

| Stated Claim | Location | Audit Finding | Status | Required Remedy |
| :--- | :--- | :--- | :--- | :--- |
| "Deep Learning model (ANN using TensorFlow/Keras) classifying Low / Moderate / High" | README.md, ml_model.py | The trained artifact `models/dl_model.h5` has a final layer `Dense(1, softmax)` and `models/label_encoder.pkl` contains only `['Low']`. Output is always 100% "Low". | `[FALSE]` | Disclose in audit; retrain a multi-class model on real, diverse crowd data in Phase 8/15. |
| "Confidence score for predictions" | README.md, ml_model.py | Because `dl_model.h5` has 1 output class with Softmax, confidence was mathematically locked to 1.0 (100%). | `[FALSE]` | Implement true multi-class probability outputs with temperature calibration. |
| "Feature engineering: count, hour, count_diff" | README.md, features.py | Features are computed, but label in `features.py` was derived deterministically from `count` (target leakage). | `[UNVERIFIED]` | Redesign activity features (speed, density, acceleration, flow) independent of static count thresholds. |
| "RandomForest model (crowd_model.pkl)" | training/train_model.py | Trained and saved to `models/crowd_model.pkl`, but never imported or called anywhere in the runtime app. | `[UNVERIFIED]` | Benchmarked as a baseline model; removed from dead-code runtime path. |

---

## 3. Backend, Telemetry, and UI Claims

| Stated Claim | Location | Audit Finding | Status | Required Remedy |
| :--- | :--- | :--- | :--- | :--- |
| "120Hz high-refresh rate interactive dashboard" | README.md, static/app.js | The browser canvas uses `requestAnimationFrame`, but monitors refresh at 60Hz on standard laptops; `120 FPS` was hardcoded text in UI. | `[FALSE]` | Measure and display true hardware render FPS dynamically; remove hardcoded 120Hz marketing text. |
| "Uptime 00:18:24 / Total Predictions 1208 / 12 faces" | static/app.js, server.py | Hardcoded in `/api/stats` and JavaScript state; randomized by `Math.random()`. | `[FALSE]` | Compute uptime from process start timestamp; compute statistics from database records. |
| "In-browser neural inference (client ANN)" | README.md, static/app.js | JavaScript fallback was a static `if/else` threshold block (`>= 15 High`, `>= 5 Moderate`, else `Low`). | `[FALSE]` | Accurately document as threshold heuristic fallback; use ONNX Runtime Web if browser inference is desired. |
| "AI-generated insights (LLM)" | README.md, llm.py | `llm.py` contains deterministic if/else Python string templates; no LLM, OpenAI, or transformers are invoked. | `[FALSE]` | Relabel as "Rule-Based Advisory Insights"; remove deceptive "LLM" labeling. |
