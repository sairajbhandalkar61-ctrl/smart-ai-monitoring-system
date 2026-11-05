# SENTINEL AI — Research Boundaries & Honest Technical Limitations

**Document Status:** Complete Empirical Disclosure  
**Authors:** Sairaj Bhandalkar (MITCOM-CA), Prof. Pallavi Gaikwad (MIT ADT University)  

---

## 1. Hardware & Platform Boundaries

1. **CPU Ceiling:** The system is engineered strictly for commodity multi-core CPUs (Intel Core i5-1145G7). While achieving 7–9 FPS with SSDLite320, heavy multi-camera concurrent feeds ($> 3$ streams) will exceed the host 4-core thermal and processing budget without hardware video decoders.
2. **Thermal Dissipation:** Continuous extended inference ($> 4$ hours) in thin-and-light chassis may induce minor thermal clock throttling (from 2.60 GHz down to ~1.60 GHz), reducing inference framerate by ~25%. Adaptive frame skipping is deployed to mitigate this risk.
3. **Windows DirectShow Camera Exclusivity:** DirectShow drivers lock physical camera handles to a single process. Multiple client applications cannot open the integrated webcam concurrently.

---

## 2. Computer Vision & Optical Constraints

1. **Single-View Perspective Foreshortening:** Standard horizontal webcam perspectives suffer from severe depth foreshortening. Pedestrians far from the lens appear dramatically smaller than foreground subjects, reducing detection confidence for distant subjects.
2. **Severe Crowd Occlusion:** In extremely dense crowds ($> 2.5 \text{ people/m}^2$), severe body-to-body overlap obscures torso geometry, leading to missed detections unless elevated overhead cameras are utilized.
3. **Tripwire Ambiguity during Group Crossings:** When two individuals cross the virtual tripwire side-by-side with touching bounding boxes, the IoU tracker may briefly cluster them into a single track, registering 1 entry instead of 2.

---

## 3. Data Science & Classification Scope

1. **Target Leakage in Historical Artifacts:** The historical dataset `data.csv` (941 rows of count 0–2) cannot support multi-class training without synthetic distortion. Real-world validation relies on newly extracted kinematic features and controlled video benchmarks.
2. **Probabilistic Uncertainty:** Softmax confidence scores should not be treated as calibrated Bayesian probabilities. Uncertainty margins are used to trigger human operator review rather than autonomous action.
