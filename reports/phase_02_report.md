# Phase 02 Report — Dataset and Machine Learning Pipeline Audit

**Phase:** Phase 2 — Audit Dataset and ML Pipeline  
**Date:** November 5, 2026  
**Git Commit / Tag:** Current HEAD / pending Phase 2 commit  

---

### 1. Files Inspected
- `data.csv`: Checked schema, 941 rows, missing values, duplicates, temporal intervals, label counts, and count distributions.
- `training/processed_data.csv`: Analyzed 3-row snapshot and feature representations.
- `training/features.py`: Inspected deterministic labeling heuristics and temporal feature extraction.
- `training/train_dl_model.py`: Audited `StandardScaler` fitting, train/test splitting, Keras architecture, loss function, and epoch settings.
- `training/train_model.py`: Audited RandomForest classifier training routine.
- `models/dl_model.h5`: Loaded and evaluated model weights and output layer configuration.
- `models/scaler.pkl`: Inspected scaling parameters (`mean_`, `scale_`, `n_features_in_`).
- `models/label_encoder.pkl`: Inspected encoded target class labels (`classes_`).
- `models/crowd_model.pkl`: Checked model architecture and usage.

### 2. Files Created
- `scripts/audit_dataset_and_ml.py`: Automated reproducible audit script.
- `evidence/phase_02/dataset_audit_metrics.json`: Quantitative audit metrics.
- `evidence/phase_02/dataset_audit_distributions.png`: Visual distribution plots for counts, labels, and sampling intervals.
- `evidence/phase_02/shipped_model_grid_predictions.csv`: Empirical grid evaluation of the shipped model across 8 diverse test points.
- `evidence/phase_02/processed_data_snapshot.csv`: Snapshot of original processed data.
- `docs/DATASET_DATASHEET.md`: Formal dataset datasheet following Gebru et al. standards.
- `reports/ml_audit.md`: Detailed technical ML audit report.
- `reports/phase_02_report.md`: Mandatory milestone report.

### 3. Files Modified
- None modified prior to audit (audited in clean baseline state).

### 4. Features Implemented / Verified
- **[IMPLEMENTED]** Automated dataset audit suite executing schema, null, duplicate, class, and autocorrelation checks (Evidence: `scripts/audit_dataset_and_ml.py`).
- **[IMPLEMENTED]** Grid evaluation of shipped Keras model demonstrating constant output behavior (Evidence: `evidence/phase_02/shipped_model_grid_predictions.csv`).
- **[IMPLEMENTED]** Target leakage and data leakage identification documented with mathematical explanations (Evidence: `reports/ml_audit.md`).
- **[IMPLEMENTED]** Formal Dataset Datasheet created (Evidence: `docs/DATASET_DATASHEET.md`).

### 5. Commands Executed
```powershell
python scripts/audit_dataset_and_ml.py
```

### 6. Tests Performed
- Schema verification test: Confirmed 941 rows, 3 columns, 0 nulls in `data.csv`.
- Class label verification: Confirmed 939 "Low", 2 "Low Activity", 0 "Moderate", 0 "High".
- Model grid evaluation test: Tested inputs spanning count 0..30, hour 0..22, count_diff -4..6.
- Autocorrelation calculation: Evaluated lag-1 and lag-5 Pearson autocorrelation across timestamps.

### 7. ACTUAL Test Results
- **Dataset Class Counts:** Low = 939 (99.79%), Low Activity = 2 (0.21%), Moderate = 0 (0.00%), High = 0 (0.00%).
- **Count Range:** Min = 0, Max = 2 (Count 0: 626; Count 1: 306; Count 2: 9).
- **Temporal Distribution:** 938 rows sampled within 12 minutes on 2026-05-02 (median $\Delta t = 0.11$s); 3 rows from 2026-04-07.
- **Autocorrelation:** Lag-1 = 0.7067 (high autocorrelation); Lag-5 = 0.5351.
- **Model Invariance:** Shipped `dl_model.h5` predicted `'Low'` with 100.0% confidence across all 8 grid tests (Pass: Confirmed Invariant).
- **Label Encoder:** Exactly 1 class present: `['Low']`.
- **Output Layer:** Single unit with Softmax `Dense(1, activation='softmax')`.

### 8. Errors Encountered and How They Were Fixed
- *Issue:* Inconsistent class spelling in raw dataset (`'Low Activity'` vs `'Low'`).
  *Fix:* Documented in `DATASET_DATASHEET.md` and normalized in the audit analysis without mutating original source data.
- *Issue:* Keras loading threw warning regarding compiled metrics.
  *Fix:* Handled cleanly in sandboxed audit execution; model architecture and weights inspected directly.

### 9. Unresolved Problems
- The historical dataset cannot support multi-class activity classification. In accordance with Rule R2 (no fabrication), this dataset will NOT be used to claim 3-class validation. Real video data collection and annotation are scheduled for Phase 14 & 15.

### 10. Remaining Tasks in this Phase & Human Tasks Created
- All Phase 2 audit requirements satisfied.
- No new human tasks required for Phase 2.

### 11. Deviations from Prompt
- None.

### 12. Exit-Criteria Checklist
- [x] Reproducible audit script created and executed (`scripts/audit_dataset_and_ml.py`).
- [x] Schema, missing values, duplicates, and class distribution documented.
- [x] Model artifacts evaluated across grid inputs; mathematical invariance documented.
- [x] Target and data leakage documented.
- [x] `docs/DATASET_DATASHEET.md` created.
- [x] `reports/ml_audit.md` completed.

**Status: PHASE 2 EXIT CRITERIA MET.**

### 13. Next Milestone
- Transition automatically to **PHASE 3 — CLEAN WINDOWS CPU-COMPATIBLE ENVIRONMENT**.
