# SENTINEL AI — Real-World Controlled Pilot Plan

**Institution:** MIT ADT University, Pune (MITCOM-CA)  
**Researcher:** Sairaj Bhandalkar | **Guide:** Prof. Pallavi Gaikwad  
**Scope:** Controlled Institutional Indoor Evaluation Protocol  

---

## 1. Pilot Objectives

1. Validate real-time person detection, multi-object tracking, and virtual tripwire counting under authentic institutional lighting and movement patterns.
2. Quantify edge CPU performance (framerate, latency, memory consumption) on commodity host hardware (Dell Latitude 3420).
3. Measure occupancy estimation accuracy ($\text{MAE}$, $\text{RMSE}$) against manual ground-truth counts across progressive stages.

---

## 2. Progressive Validation Stages

### Stage 1: Benchmarking via Authorized Reference Video Footage
* **Environment:** Laboratory workstation playback of representative indoor corridor video sequences.
* **Objective:** Verify pipeline execution, tripwire line crossings, and tracker stability under known ground truth.

### Stage 2: Controlled Single-Subject Live Validation
* **Environment:** Faculty office / controlled computer laboratory.
* **Objective:** Single volunteer walking into and out of camera frame across the virtual tripwire at varying angles and speeds.
* **Tasks:** Validate DirectShow ingestion, bounding box tightness, track continuity, and entry/exit registration.

### Stage 3: Multi-Subject Indoor Corridor Pilot
* **Environment:** Departmental corridor during lecture transition intervals.
* **Authorization:** Departmental approval required (`HT-003`); conspicuous signage posted indicating automated aggregate occupancy testing without identity recording.
* **Ground Truth Protocol:** A designated manual counter tallies pedestrian entries and exits using an independent hand tally counter during 10-minute observation windows.
* **Metrics:**
  $$\text{MAE} = \frac{1}{N}\sum_{i=1}^N |Y_{\text{true}} - \hat{Y}_{\text{pred}}|$$
  $$\text{Accuracy}_{\text{Tripwire}} = \left(1 - \frac{|\Delta_{\text{entries}}| + |\Delta_{\text{exits}}|}{\text{Total Transitions}}\right) \times 100\%$$

---

## 3. Risk Mitigation & Privacy Compliance

* No footage recorded or archived during public pilot sessions.
* Real-time blurred visual stream displayed to operators.
* Immediate pilot termination upon administrative request or hardware thermal throttle threshold ($> 85^\circ\text{C}$).
