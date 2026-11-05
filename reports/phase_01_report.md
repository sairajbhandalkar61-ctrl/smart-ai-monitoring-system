# Phase 01 Report — Repository and Hardware Audit

**Phase:** Phase 1 — Inspect Repository and Hardware  
**Date:** November 5, 2026  
**Git Commit / Tag:** `e6b216e` / `baseline-original`  

---

### 1. Files Inspected
- `data.csv`: Inspected shape (941, 3), column values, distributions, and timestamps.
- `detection.py`: Analyzed Haar cascade loading, grayscale conversion, equalization, and NMS fusion.
- `ml_model.py`: Inspected model loading, feature scaling, inference, and classification logic.
- `training/features.py`: Inspected feature calculation and deterministic rule labeling.
- `training/processed_data.csv`: Inspected shape (3, 5) and sample values.
- `training/train_dl_model.py`: Inspected StandardScaler fitting, Keras Sequential architecture, and training routine.
- `training/train_model.py`: Inspected RandomForest training script.
- `app.py`: Inspected Streamlit structure, while loop, and fallback image behavior.
- `server.py`: Inspected FastAPI endpoints (`/api/predict`, `/api/detect`, `/api/stats`, `/api/snapshot`).
- `static/app.js` & `static/index.html`: Inspected canvas animation loop, telemetry timers, and fallback heuristics.
- `models/dl_model.h5`, `models/scaler.pkl`, `models/label_encoder.pkl`: Loaded and verified model topology and class encoder.

### 2. Files Created
- `evidence/phase_01/original_files_sha256.csv`: Cryptographic hashes for all 32 original baseline files.
- `evidence/phase_01/hardware_discovery.json`: Structured hardware and platform inventory.
- `docs/HARDWARE_PROFILE.md`: Documented Dell Latitude 3420 hardware specifications and implications.
- `scripts/doctor.ps1`: Automated environment and hardware diagnostic tool.
- `docs/DECISIONS.md`: Initial Architecture Decision Records (ADR-001 through ADR-004).
- `docs/HUMAN_TASKS.md`: Catalog of physical human tasks (`HT-001` through `HT-005`).
- `docs/claims_audit.md`: Detailed audit comparing claims vs verified facts vs false claims.
- `docs/KNOWN_LIMITATIONS.md`: Formal log of technical, machine learning, and operational constraints.
- `docs/AUDIT_REPORT.md`: Comprehensive audit report covering vision, ML, security, and backend.
- `PROJECT_STATE.md`: Persistent execution ledger tracking phase progress and exit criteria.
- `.gitignore`: Configured to exclude virtual environments, cache, backups, and sensitive data.
- `reports/phase_01_report.md`: Mandatory milestone report.

### 3. Files Modified
- None modified prior to baseline capture (pristine snapshot preserved and tagged `baseline-original`).

### 4. Features Implemented / Attempted
- **[IMPLEMENTED]** Complete baseline backup created at `c:\Users\Admin\Downloads\sentinel_original_backup` (Evidence: Directory check & `evidence/phase_01/original_files_sha256.csv`).
- **[IMPLEMENTED]** Automated hardware discovery script (Evidence: `evidence/phase_01/hardware_discovery.json`).
- **[IMPLEMENTED]** Automated environment doctor diagnostic tool (Evidence: `scripts/doctor.ps1`).
- **[IMPLEMENTED]** Git repository initialization with `baseline-original` immutable tag (Evidence: `git tag -l`).
- **[IMPLEMENTED]** Full technical, ML, and claims audit completed (Evidence: `docs/AUDIT_REPORT.md` and `docs/claims_audit.md`).

### 5. Commands Executed
```powershell
# Backup original tree
Copy-Item -Path "c:\Users\Admin\Downloads\smart-ai-monitoring-system-main\*" -Destination "c:\Users\Admin\Downloads\sentinel_original_backup" -Recurse -Force -Exclude "repo_clone",".git"

# Compute SHA256 of all baseline files
Get-FileHash -Path $f.FullName -Algorithm SHA256 | Export-Csv "evidence\phase_01\original_files_sha256.csv"

# Hardware discovery
Get-CimInstance Win32_Processor, Win32_ComputerSystem, Win32_OperatingSystem, Win32_VideoController
Get-PnpDevice -Class Camera, Image
powercfg /getactivescheme

# Git baseline commit and tagging
git init
git add -A
git commit -m "chore(baseline): Initial pristine repository snapshot with hardware discovery and claims audit"
git tag -a baseline-original -m "Baseline original state of SENTINEL AI project before refactoring"
```

### 6. Tests Performed
- Verification of file hashes in `evidence/phase_01/original_files_sha256.csv`.
- Diagnostic execution of `scripts/doctor.ps1` to confirm camera, CPU, RAM, and disk reporting.
- Verification of git tag existence via `git tag -l`.

### 7. ACTUAL Test Results
- **File Hashing:** 32 baseline files verified and hashed (Pass: 32/32).
- **Hardware Doctor:** Successfully identified Dell Latitude 3420, i5-1145G7 CPU, 7.74 GB RAM, Intel Iris Xe graphics, and integrated webcam (Pass: 5/5).
- **Git Baseline Tag:** Tag `baseline-original` created at commit `e6b216e` (Pass).

### 8. Errors Encountered and How They Were Fixed
- *Issue:* Git repository was previously uninitialized at the root folder (only present in a nested subfolder).
  *Fix:* Initialized git at the root folder, configured `.gitignore` to exclude nested `repo_clone` and cache, and committed the clean baseline.
- *Issue:* Background task timeout during hardware JSON serialization.
  *Fix:* Managed task execution via `manage_task` status checks, successfully capturing output.

### 9. Unresolved Problems
- None in Phase 1 scope. (Identified architectural defects in the legacy codebase are cataloged in `docs/KNOWN_LIMITATIONS.md` to be addressed in subsequent phases).

### 10. Remaining Tasks in this Phase & Human Tasks Created
- All Phase 1 engineering tasks complete.
- Human Tasks created: `HT-001` (Windows camera permissions), `HT-002` (webcam validation volunteer).

### 11. Deviations from Prompt
- None.

### 12. Exit-Criteria Checklist
- [x] Full tree backup outside working tree exists (`sentinel_original_backup`).
- [x] SHA-256 baseline hashes computed and recorded.
- [x] Git initialized, pristine baseline committed and tagged `baseline-original`.
- [x] Hardware specifications verified (Dell Latitude 3420, i5-1145G7, 7.74 GB RAM, Intel Iris Xe).
- [x] Claims audit (`docs/claims_audit.md`) and technical audit (`docs/AUDIT_REPORT.md`) created.
- [x] Known limitations documented (`docs/KNOWN_LIMITATIONS.md`).
- [x] ADRs initialized (`docs/DECISIONS.md`).
- [x] Diagnostic tool implemented (`scripts/doctor.ps1`).

**Status: PHASE 1 EXIT CRITERIA MET.**

### 13. Next Milestone
- Transition automatically to **PHASE 2 — AUDIT DATASET AND ML PIPELINE**.
