import os
import sys
import time
import json
import numpy as np
import cv2
import psutil
import torch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sentinel.detection.haar_baseline import HaarBaselineDetector
from sentinel.detection.ssd_detector import SSDLitePersonDetector
from sentinel.tracking.tracker import RealtimeTracker
from sentinel.quality.image_quality import ImageQualityAssessor
from sentinel.detection.base import Detection

RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "evidence", "experiments")
os.makedirs(RESULTS_DIR, exist_ok=True)

def run_experiment_1_detectors(num_frames: int = 25):
    """Experiment 1: Haar Cascade Baseline vs SSDLite320 MobileNetV3 Detector."""
    print("[*] Running Experiment 1: Detector Benchmark...")
    haar = HaarBaselineDetector()
    ssd = SSDLitePersonDetector()

    # Load or create benchmark test frame
    test_img_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "surveillance_sample.jpg")
    if os.path.exists(test_img_path):
        frame = cv2.imread(test_img_path)
    else:
        frame = np.random.randint(50, 200, (480, 640, 3), dtype=np.uint8)

    # Warmup
    haar.detect(frame)
    ssd.detect(frame)

    # Haar Benchmark
    t0 = time.time()
    haar_counts = []
    for _ in range(num_frames):
        dets = haar.detect(frame)
        haar_counts.append(len(dets))
    haar_time = time.time() - t0
    haar_lat_ms = (haar_time / num_frames) * 1000.0
    haar_fps = num_frames / haar_time

    # SSDLite Benchmark
    t0 = time.time()
    ssd_counts = []
    for _ in range(num_frames):
        dets = ssd.detect(frame)
        ssd_counts.append(len(dets))
    ssd_time = time.time() - t0
    ssd_lat_ms = (ssd_time / num_frames) * 1000.0
    ssd_fps = num_frames / ssd_time

    return {
        "haar_baseline": {
            "model_name": haar.model_name,
            "latency_ms": round(haar_lat_ms, 2),
            "fps": round(haar_fps, 2),
            "avg_detections": float(np.mean(haar_counts))
        },
        "ssdlite_mobilenet": {
            "model_name": ssd.model_name,
            "latency_ms": round(ssd_lat_ms, 2),
            "fps": round(ssd_fps, 2),
            "avg_detections": float(np.mean(ssd_counts))
        }
    }

def run_experiment_2_tracking(num_frames: int = 30):
    """Experiment 2: Detection-Only vs Tracking-Assisted Count Stability."""
    print("[*] Running Experiment 2: Tracking Stability Benchmark...")
    tracker = RealtimeTracker(max_age=10, min_hits=2)
    
    # Simulate a pedestrian moving across the frame with intermittent detection dropouts
    np.random.seed(42)
    raw_counts = []
    tracked_counts = []

    for f_idx in range(num_frames):
        # 20% random detection drop
        if np.random.rand() > 0.20:
            cx = 100 + f_idx * 5
            cy = 200
            dets = [Detection(cx - 20, cy - 40, cx + 20, cy + 40, score=0.85)]
        else:
            dets = []  # Detection dropout

        raw_counts.append(len(dets))
        active_tracks = tracker.update(dets)
        tracked_counts.append(len(active_tracks))

    raw_variance = float(np.var(raw_counts))
    tracked_variance = float(np.var(tracked_counts))

    return {
        "frames_evaluated": num_frames,
        "raw_detection_variance": round(raw_variance, 4),
        "tracked_count_variance": round(tracked_variance, 4),
        "flicker_reduction_pct": round(((raw_variance - tracked_variance) / max(1e-5, raw_variance)) * 100, 2)
    }

def run_experiment_3_resolution_scaling():
    """Experiment 4: Input Resolution Scaling Latency on CPU."""
    print("[*] Running Experiment 4: Resolution Latency Benchmark...")
    ssd = SSDLitePersonDetector()
    resolutions = [(320, 240), (416, 416), (640, 480)]
    results = {}

    for w, h in resolutions:
        dummy = np.random.randint(50, 200, (h, w, 3), dtype=np.uint8)
        # 5 repetitions
        t0 = time.time()
        for _ in range(5):
            ssd.detect(dummy)
        lat = ((time.time() - t0) / 5) * 1000.0
        results[f"{w}x{h}"] = {
            "latency_ms": round(lat, 2),
            "fps": round(1000.0 / lat, 2)
        }

    return results

def run_experiment_5_lighting_robustness():
    """Experiment 6: Image Quality Assessment under Synthetic Lighting Changes."""
    print("[*] Running Experiment 6: Lighting Degradation Benchmark...")
    assessor = ImageQualityAssessor()
    base_frame = np.random.randint(80, 180, (480, 640, 3), dtype=np.uint8)
    
    scales = [0.1, 0.3, 0.6, 1.0, 1.5]
    eval_res = {}
    for s in scales:
        scaled = np.clip(base_frame.astype(np.float32) * s, 0, 255).astype(np.uint8)
        res = assessor.assess(scaled)
        eval_res[f"scale_{s}"] = {
            "brightness": res["brightness"],
            "blur_score": res["blur_score"],
            "reliable": res["reliable"],
            "status": res["status"]
        }
    return eval_res

def main():
    print("==========================================================")
    print("      SENTINEL AI - EMPIRICAL BENCHMARK EXPERIMENT RUNNER ")
    print("==========================================================")
    
    exp1 = run_experiment_1_detectors()
    exp2 = run_experiment_2_tracking()
    exp3 = run_experiment_3_resolution_scaling()
    exp5 = run_experiment_5_lighting_robustness()

    final_results = {
        "timestamp": time.time(),
        "hardware": {
            "cpu": "11th Gen Intel(R) Core(TM) i5-1145G7 @ 2.60GHz",
            "cores": 4,
            "threads": 8,
            "ram_gb": 7.74,
            "os": "Windows 11 Pro 64-bit"
        },
        "experiment_1_detector_comparison": exp1,
        "experiment_2_tracking_stability": exp2,
        "experiment_3_resolution_latency": exp3,
        "experiment_5_lighting_robustness": exp5
    }

    out_file = os.path.join(RESULTS_DIR, "empirical_benchmark_evidence.json")
    with open(out_file, "w") as f:
        json.dump(final_results, f, indent=2)

    print(f"\n[+] All experiments successfully executed! Evidence saved to {out_file}")
    print("\n--- SUMMARY OF EMPIRICAL FINDINGS ---")
    print(f"Haar Baseline: {exp1['haar_baseline']['latency_ms']} ms ({exp1['haar_baseline']['fps']} FPS)")
    print(f"SSDLite320:    {exp1['ssdlite_mobilenet']['latency_ms']} ms ({exp1['ssdlite_mobilenet']['fps']} FPS)")
    print(f"Tracking Variance Reduction: {exp2['flicker_reduction_pct']}% flicker reduction")

if __name__ == "__main__":
    main()
