# Dataset Datasheet — SENTINEL AI Baseline Dataset (`data.csv`)

Following the standard framework for *Datasheets for Datasets* (Gebru et al., 2021).

---

## 1. Motivation

* **For what purpose was the dataset created?**  
  The dataset was collected to record temporal person detection counts from a webcam setup and train an activity classification model for the Smart AI Monitoring System.
* **Who created the dataset?**  
  Sairaj Bhandalkar (MIT ADT University).

---

## 2. Composition

* **What do the instances that comprise the dataset represent?**  
  Each record represents a timestamped observation from an OpenCV detection process.
* **How many instances are there in total?**  
  941 rows.
* **What are the attributes/features?**  
  1. `time`: ISO timestamp string (e.g., `2026-05-02 12:36:14.123456`).
  2. `count`: Integer detected person/face count (`0`, `1`, or `2`).
  3. `activity`: String target classification label (`Low` or `Low Activity`).
* **Is there missing data?**  
  No missing values (0 nulls across all 3 columns).
* **Are there duplicates?**  
  No exact duplicate rows across all 3 columns, but 938 rows share near-identical features (`count` is either 0 or 1 with sub-second interval differences).
* **Class distribution:**  
  * `Low`: 939 instances (99.79%)  
  * `Low Activity`: 2 instances (0.21%)  
  * `Moderate`: 0 instances (0.00%)  
  * `High`: 0 instances (0.00%)  
* **Count distribution:**  
  * `count = 0`: 626 instances (66.5%)  
  * `count = 1`: 306 instances (32.5%)  
  * `count = 2`: 9 instances (1.0%)  
  * Maximum count observed: `2`

---

## 3. Collection Process

* **How was the data collected?**  
  Logged automatically from OpenCV face detection runs on a laptop webcam across two recording intervals:
  * Session 1 (2026-04-07 18:14 to 18:25): 3 samples (Hour 18).
  * Session 2 (2026-05-02 12:36 to 12:48): 938 samples (Hour 12), with a median sampling interval of 0.11 seconds.
* **Temporal characteristics:**  
  The dataset exhibits extreme temporal autocorrelation (lag-1 autocorrelation = 0.7067; lag-5 = 0.5351) because successive video frames sampled at ~9 FPS capture the same stationary scene.
* **Gaps:**  
  A 594.2-hour temporal gap exists between the first 3 rows and the remaining 938 rows.

---

## 4. Known Critical Limitations & Flaws

1. **Complete Class Imbalance (Single-Class Degeneracy):** The dataset contains effectively one class (`Low`). It is mathematically impossible to train a valid three-class (`Low`, `Moderate`, `High`) classifier on this dataset alone.
2. **Label Inconsistency:** Two rows are labeled `"Low Activity"` instead of `"Low"`.
3. **Severe Density Truncation:** Maximum count is 2. The dataset contains zero examples of medium or dense crowds.
4. **Hour Representation:** Only hours 12 and 18 are present. Standardizing hour over this distribution causes severe out-of-distribution scaling anomalies when queried at any of the other 22 hours of the day.

---

## 5. Usage Guidelines & Protocol

* **Permitted Use:** Historical baseline documentation and audit benchmark only.
* **Prohibited Use:** Must NOT be used to claim validation of a 3-class crowd activity neural network.
* **Remediation Plan:** Real-world validation (Phase 14) and synthetic augmentation/annotated video benchmarks (Phase 15) must supply balanced multi-class observations before any scientific claims on activity classification are made.
