# Known Technical Limitations & Constraints

This living document transparently records verified system limitations, architectural constraints, and open engineering challenges in SENTINEL AI.

---

## 1. Hardware & Platform Limitations

1. **No Discrete GPU (CPU-Only Constraint):** The host device is an Intel Core i5-1145G7 with integrated Intel Iris Xe Graphics. Large vision models (e.g., YOLOv8x, Faster R-CNN) cannot achieve interactive framerates (>15 FPS). All candidate models must be evaluated under strict CPU thread budgets.
2. **Webcam Device Locks on Windows:** DirectShow (`CAP_DSHOW`) and Media Foundation (`CAP_MSMF`) drivers on Windows do not support multi-process concurrent access. If a process does not cleanly release `cv2.VideoCapture`, subsequent attempts fail until the process terminates.
3. **Thermal Throttling Under Extended CPU Load:** Sustained 100% CPU utilization across all 8 threads on a thin-and-light laptop triggers power and thermal throttling, dropping clock speed from 2.60 GHz to ~1.50 GHz. Frame skipping and tracker extrapolation are necessary to prevent thermal degradation.

---

## 2. Computer Vision & Detection Limitations

1. **Haar Cascade False Positives and Occlusion Failure:** Classical Haar cascades rely on rigid rectangular intensity patterns. They suffer significant false positives in complex textured backgrounds and fail when subjects turn beyond 45 degrees or are partially occluded.
2. **Face/Upper-Body Count vs. Person Count Disparity:** Detecting faces does not equal detecting people. When people walk with their backs to the camera, look down at phones, or wear masks/hoodies, face detectors completely miss them. Person body detectors are required for valid crowd counting.
3. **Surveillance Angle Domain Gap:** A desk-level laptop webcam has a near-horizontal perspective, causing extreme scale variation and foreshortening compared to ceiling-mounted surveillance cameras (elevated 30–45 degrees).

---

## 3. Data & Machine Learning Limitations

1. **Monolithic Single-Class Training Dataset (`data.csv`):** The provided historical dataset contains 941 rows, of which 939 are labeled "Low" and 2 "Low Activity". All 941 counts are between 0 and 2. It contains zero examples of Moderate or High crowd density.
2. **Target Leakage by Construction in Legacy ANN:** In `training/features.py`, the target activity label was generated directly via an `if count >= 5` rule. Training an ANN on features `[count, hour, count_diff]` simply approximates this rule rather than learning intrinsic crowd behavior.
3. **Single Output Neuron in Shipped Artifact:** The shipped `dl_model.h5` model has output shape `(None, 1)` with a `softmax` activation, resulting in mathematical invariance (always predicting 100% confidence for class 0).
4. **Data Leakage in Standardization:** In `training/train_dl_model.py`, `StandardScaler.fit_transform()` was executed on the complete dataset prior to `train_test_split()`, leaking distribution statistics from the test partition into the training partition.

---

## 4. Operational & Deployment Limitations

1. **Absence of Authentication in Legacy Server:** Legacy `server.py` had no authentication or authorization layer, allowing arbitrary clients to trigger detection and save snapshots.
2. **Browser-Only Demo Fallback:** The GitHub Pages deployment runs statically without a Python backend, relying on client-side simulation.
