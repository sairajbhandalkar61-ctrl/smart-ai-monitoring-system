# Architecture Decision Records (ADRs)

All significant technical decisions, trade-offs, and design commitments are recorded here with date, context, alternatives considered, chosen decision, and consequences.

---

## ADR-001: Strict CPU-Only Baseline with Modular Inference Backends
* **Date:** 2026-11-05
* **Status:** Accepted
* **Context:** The development machine is a Dell Latitude 3420 with an 11th Gen Intel Core i5-1145G7 CPU and integrated Intel Iris Xe graphics. No NVIDIA GPU or CUDA is present.
* **Options Considered:**
  1. Mandate NVIDIA GPU / CUDA (Would make local execution impossible).
  2. Pure CPU execution using lightweight ONNX Runtime / OpenCV DNN / PyTorch CPU with optional OpenVINO acceleration.
* **Decision:** Enforce CPU as the non-negotiable required baseline. All detectors and classifiers must run comfortably on multi-threaded CPU without requiring external GPU hardware. OpenVINO is supported as an optional accelerator with automatic fallback to CPU.
* **Consequences:** Models must be lightweight (nano/small variants, input resolutions 320–640). Heavy architectures (e.g. YOLOv8x, Faster R-CNN with ResNet101) are excluded from the default pipeline.

---

## ADR-002: Decoupled Edge Worker, API, and Dashboard Architecture
* **Date:** 2026-11-05
* **Status:** Accepted
* **Context:** The legacy implementation ran camera capture inside a blocking Streamlit while-loop and inside synchronous FastAPI route handlers, causing UI freezing, event loop blockage, and inability to cleanly restart cameras.
* **Options Considered:**
  1. Monolithic Streamlit app with embedded OpenCV loop.
  2. Decoupled architecture: Native Windows Edge Worker for capture & inference -> Core FastAPI backend with database persistence -> Streamlit / Web UI consuming API and MJPEG stream.
* **Decision:** Adopt the decoupled architecture. The native Edge Worker handles camera I/O, detection, tracking, and telemetry streaming. Streamlit consumes the backend API and embeds an MJPEG stream.
* **Consequences:** Eliminates UI freezing, isolates camera crashes, allows headless server deployments, and supports multiple camera feeds.

---

## ADR-003: Strict Separation of Research Paper from Development Phases
* **Date:** 2026-11-05
* **Status:** Accepted
* **Context:** Scientific integrity requires that research papers report verified, reproducible experimental evidence rather than unverified initial claims.
* **Options Considered:**
  1. Draft the manuscript concurrently with initial development.
  2. Complete Phases 1 through 15 (implementation, real webcam validation, tracking, occupancy, leakage-free ANN, optimization, and scientific experiments) and freeze results BEFORE drafting the final manuscript in Phase 16.
* **Decision:** Strictly enforce sequential completion. No research paper text is finalized until Phase 15 experimental results are tagged and frozen.
* **Consequences:** Guarantees 100% academic integrity; every metric, table, and figure in the final paper will originate directly from executed code and reproducible logs.

---

## ADR-004: Explicit Labeling of Estimates vs. Ground Truth and Elimination of Fabricated Data
* **Date:** 2026-11-05
* **Status:** Accepted
* **Context:** The legacy frontend and API returned hardcoded values (12 faces, 120 FPS, 1208 predictions) and random-walk fluctuations.
* **Options Considered:**
  1. Retain simulated numbers for visual demonstration.
  2. Remove all hardcoded fake values from production endpoints. Any demo mode must be explicitly separated and visibly labeled "SIMULATED / DEMO DATA".
* **Decision:** Enforce truth in telemetry. All counts are labeled as "ESTIMATES". Hardcoded statistics are completely eliminated.
* **Consequences:** Ensures compliance with research integrity rules R4, R5, and R6.
