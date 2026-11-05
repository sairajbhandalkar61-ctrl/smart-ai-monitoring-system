# Human Tasks and Physical Verification Log

This document records physical human actions, approvals, and manual verification steps that cannot be automated by software agents.
**Rule:** The agent will NEVER block on these tasks. All independent engineering, testing, optimization, and synthesis will proceed unblocked. Results dependent on human physical actions will be labeled `[PENDING]`.

---

| Task ID | Required Action | Target Phase | Rationale | Status |
| :--- | :--- | :--- | :--- | :--- |
| **HT-001** | Grant Windows Camera Permission to Python / Terminal | Phase 4 | Required for the laptop webcam to be accessed by `cv2.VideoCapture` without OS-level permission rejection. | `[PENDING]` (Will test via CLI) |
| **HT-002** | Volunteer in front of webcam during real validation | Phase 4 / 5 / 14 | Provides real human subject in front of camera for live detection and tracking verification. | `[PENDING]` |
| **HT-003** | Provide institutional campus pilot authorization / consent | Phase 14 | Required if recorded or live video is captured in public university campus spaces (MIT ADT University). | `[PENDING]` (Controlled indoor testing used as fallback) |
| **HT-004** | Ground-truth annotation of test video clips | Phase 5 / 8 / 15 | Human labeling of person counts on sample frames for MAE/RMSE benchmark calculations. | `[PENDING]` (Annotation script provided in Phase 8) |
| **HT-005** | Final review and signature of Research Manuscript | Phase 16 / 17 | Author (Sairaj Bhandalkar) and Guide (Prof. Pallavi Gaikwad) academic review before submission. | `[PENDING]` |
