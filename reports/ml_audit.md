# SENTINEL AI — Machine Learning Pipeline & Artifact Audit Report

**Report Location:** `reports/ml_audit.md`  
**Execution Date:** November 5, 2026  
**Evidence Artifacts:**  
* `evidence/phase_02/dataset_audit_metrics.json`
* `evidence/phase_02/dataset_audit_distributions.png`
* `evidence/phase_02/shipped_model_grid_predictions.csv`
* `evidence/phase_02/processed_data_snapshot.csv`
* `docs/DATASET_DATASHEET.md`

---

## 1. Executive Summary

This audit rigorously evaluated the shipped dataset (`data.csv`, `processed_data.csv`), feature extraction scripts (`training/features.py`), model training pipelines (`training/train_dl_model.py`, `train_model.py`), and saved serializations (`models/dl_model.h5`, `scaler.pkl`, `label_encoder.pkl`, `crowd_model.pkl`).

### Verified Core Findings:
1. **Mathematical Invariance of Shipped ANN:** When queried across an 8-point parameter grid (counts 0 to 30, hours 0 to 22, count_diff -4 to +6), the shipped neural model predicted **"Low" with 100.0% confidence in 100% of cases**. The output vector was identically `[1.0]` across all inputs.
2. **Root Cause Identified:** The shipped model topology consists of:
   * `Input(3)` -> `Dense(16, relu)` -> `Dense(8, relu)` -> `Dense(1, softmax)`.
   * A Softmax activation applied to a single scalar node $z$ computes $\frac{e^z}{e^z} = 1.0$ by mathematical definition.
   * `label_encoder.pkl` contains exclusively one class: `['Low']`.
3. **Target Leakage by Construction:** In `training/features.py`, the activity label is produced via an explicit heuristic on `count`:
   ```python
   if count >= 5: return 'High'
   elif count >= 2: return 'Moderate'
   else: return 'Low'
   ```
   Because `count` is simultaneously an input feature, the neural network was simply tasked with learning an if-else decision boundary rather than genuine crowd activity dynamics.
4. **Data Leakage in Standardization:** In `training/train_dl_model.py`, `StandardScaler.fit_transform()` was called on the entire dataset prior to splitting, contaminating test metrics with training distribution statistics.
5. **Autocorrelation & Temporal Gaps:** 99.7% of the data originated from a single 12-minute webcam recording on 2026-05-02 with sub-second spacing (lag-1 autocorrelation = 0.7067). Random train/test splitting on such data causes severe optimistic test bias due to near-identical frames being split between train and test partitions.

---

## 2. Experimental Grid Evidence

The shipped model artifacts were tested using `scripts/audit_dataset_and_ml.py` without modifying model weights. The empirical results are recorded below:

| Count | Hour | Count Diff | Model Raw Output | Predicted Label | Confidence (%) |
| :---: | :---: | :---: | :---: | :---: | :---: |
| 0 | 12 | 0 | `[1.0]` | Low | 100.0% |
| 1 | 18 | 0 | `[1.0]` | Low | 100.0% |
| 2 | 18 | 1 | `[1.0]` | Low | 100.0% |
| 5 | 14 | 3 | `[1.0]` | Low | 100.0% |
| 12 | 10 | 2 | `[1.0]` | Low | 100.0% |
| 18 | 18 | 5 | `[1.0]` | Low | 100.0% |
| 25 | 20 | -4 | `[1.0]` | Low | 100.0% |
| 30 | 22 | 6 | `[1.0]` | Low | 100.0% |

**Audit Conclusion:** The claim in the original `README.md` of a validated multi-class (Low/Moderate/High) deep learning model is **empirically false** for the shipped artifacts.

---

## 3. Required Remediation Protocol (Enforced in Phase 8 & 15)

1. **Independent Activity Definition:** Crowd activity must be derived from kinematic multi-object track dynamics (speed variance, flow rate, directional entropy, spatial density) rather than a circular count threshold.
2. **Blocked Temporal Cross-Validation:** Video sessions must be partitioned by continuous temporal blocks (GroupKFold by session), preventing identical adjacent frames from bridging train and test splits.
3. **Strict Preprocessing Isolation:** Fit `StandardScaler` strictly on training folds and apply `.transform()` on test folds.
4. **Multi-Class Evaluation:** Validate on genuinely diverse, annotated video clips (Phase 14/15) spanning real low, moderate, and high crowd densities.
