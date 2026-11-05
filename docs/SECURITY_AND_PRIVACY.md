# SENTINEL AI — Security, Privacy, and Responsible AI Protocol

---

## 1. Ethical Stance and System Boundaries

SENTINEL AI is strictly designed as an **institutional facility intelligence and aggregate occupancy estimation system**. It is explicitly **not** an individual biometric surveillance, facial recognition, or law-enforcement tool.

### Absolute System Prohibitions:
1. **No Facial Recognition:** No feature vectors, embeddings, or facial signatures are extracted, stored, or compared against any identity database.
2. **No Biometric Identification:** Pedestrians are processed solely as volumetric human shapes.
3. **No Individual Behavioral Tracking:** Movement analysis is strictly spatial and kinematic (measuring bulk crowd flux, density, and velocity dispersion), not personal profiling.
4. **No Permanent Raw Video Storage:** In-memory frames are processed and immediately discarded. No video files or raw frames are written to persistent storage unless explicitly activated for offline model benchmarking with participant consent.

---

## 2. Privacy-by-Design Technical Controls

* **Ephemeral Temporary Track Identifiers:** Tracks receive arbitrary integer tokens (`ID #1`, `ID #2`) assigned chronologically within active memory. Identifiers expire after 15 consecutive missing frames and reset upon pipeline reinitialization.
* **Local Edge Processing:** All inference runs natively on the local Intel CPU without transmitting video frames to third-party cloud APIs.
* **Data Minimization:** Only structured numerical telemetry (`timestamp`, `count`, `entries`, `exits`, `activity_class`, `blur_score`) is persisted to SQLite.

---

## 3. Human-in-the-Loop Safeguards

* **No Automated Decision Enforcement:** SENTINEL AI does not trigger autonomous access locks, automated physical doors, or security dispatch.
* **Uncertainty Flagging:** Ambiguous predictions (confidence $< 60\%$) and poor visual quality (blur $> 60$, low light) trigger `"Verification Recommended"` alerts rather than presenting false certainty to operators.
* **Manual Drift Reconciliation:** Facility administrators retain sole authority to adjust occupancy baseline figures via the dashboard interface.
