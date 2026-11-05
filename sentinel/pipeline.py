import time
import threading
import cv2
import numpy as np
import psutil
from typing import Optional, Dict, Any, List

from sentinel.capture.video_stream import ResilientVideoStream
from sentinel.quality.image_quality import ImageQualityAssessor
from sentinel.detection.base import BaseDetector, Detection
from sentinel.detection.ssd_detector import SSDLitePersonDetector
from sentinel.detection.haar_baseline import HaarBaselineDetector
from sentinel.tracking.tracker import RealtimeTracker, Track
from sentinel.occupancy.tripwire import TripwireLine
from sentinel.occupancy.zones import ZoneManager
from sentinel.activity.classifier import ActivityClassifier
from sentinel.alerts.engine import AlertEngine
from sentinel.storage.database import DatabaseManager

class SentinelPipeline:
    """
    Modular End-to-End Vision and Intelligence Pipeline.
    Orchestrates acquisition, quality, detection, tracking, zones, tripwires,
    activity classification, alerts, and database telemetry.
    """
    def __init__(
        self,
        camera_src: int | str = 0,
        detector_type: str = "ssdlite",
        frame_width: int = 640,
        frame_height: int = 480,
        adaptive_sampling: bool = True
    ):
        self.camera_src = camera_src
        self.detector_type = detector_type
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.adaptive_sampling = adaptive_sampling

        # Components
        self.stream = ResilientVideoStream(src=camera_src, backend="DSHOW", width=frame_width, height=frame_height)
        self.quality = ImageQualityAssessor()
        
        # Detector selection
        if detector_type.lower() == "haar":
            self.detector: BaseDetector = HaarBaselineDetector()
        else:
            self.detector: BaseDetector = SSDLitePersonDetector()

        self.tracker = RealtimeTracker(max_age=15, min_hits=2, iou_threshold=0.3)
        self.tripwire = TripwireLine(y_fraction=0.50, frame_height=frame_height, frame_width=frame_width)
        self.zones = ZoneManager(width=frame_width, height=frame_height)
        self.activity_classifier = ActivityClassifier()
        self.alert_engine = AlertEngine(cooldown_seconds=30.0)
        self.db = DatabaseManager()

        # Pipeline loop state
        self.running = False
        self.lock = threading.Lock()
        self.worker_thread: Optional[threading.Thread] = None
        
        # Latest frame buffers
        self.latest_raw_frame: Optional[np.ndarray] = None
        self.latest_annotated_frame: Optional[np.ndarray] = None
        
        # Metrics & Telemetry
        self.processed_frames = 0
        self.pipeline_fps = 0.0
        self.inference_latency_ms = 0.0
        self.end_to_end_latency_ms = 0.0
        self.cpu_usage_pct = 0.0
        self.mem_usage_mb = 0.0
        
        # Latest states
        self.current_detections: List[Detection] = []
        self.current_tracks: List[Track] = []
        self.current_quality: Dict[str, Any] = {}
        self.current_activity: Dict[str, Any] = {
            "activity": "Low Activity",
            "confidence": 1.0,
            "status": "Low Activity",
            "is_uncertain": False
        }
        self.prev_count = 0
        self.last_db_save = time.time()

    def start(self):
        with self.lock:
            if self.running:
                return
            self.stream.start()
            self.running = True
            self.worker_thread = threading.Thread(target=self._pipeline_loop, daemon=True)
            self.worker_thread.start()

    def stop(self):
        self.running = False
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=2.0)
        self.stream.stop()

    def set_detector(self, detector_type: str):
        with self.lock:
            if detector_type.lower() == "haar":
                self.detector = HaarBaselineDetector()
                self.detector_type = "haar"
            else:
                self.detector = SSDLitePersonDetector()
                self.detector_type = "ssdlite"

    def _pipeline_loop(self):
        fps_counter = 0
        fps_timer = time.time()
        frame_interval = 2  # default skip
        
        process = psutil.Process()

        while self.running:
            loop_start = time.time()
            success, frame, frame_id = self.stream.read()
            if not success or frame is None:
                time.sleep(0.02)
                continue

            # 1. Quality Assessment
            quality_info = self.quality.assess(frame)
            with self.lock:
                self.current_quality = quality_info

            if not quality_info["reliable"]:
                self.alert_engine.trigger(
                    alert_type="quality_warning",
                    severity="warning",
                    title="Degraded Visual Quality",
                    description=quality_info["status"]
                )

            # 2. Adaptive Frame Scheduling
            # If scene is active or count changed, sample more frequently
            if self.adaptive_sampling:
                if len(self.current_tracks) > 0 or quality_info["is_blurry"]:
                    frame_interval = 1  # high alert, inspect every frame
                else:
                    frame_interval = 3  # quiescent scene, reduce CPU load
            else:
                frame_interval = 2

            # Check if this frame should run heavy DL inference
            run_detection = (frame_id % frame_interval == 0)

            detections = []
            if run_detection:
                t_det0 = time.time()
                detections = self.detector.detect(frame)
                self.inference_latency_ms = (time.time() - t_det0) * 1000.0
                with self.lock:
                    self.current_detections = detections

            # 3. Multi-Object Tracking
            active_tracks = self.tracker.update(detections if run_detection else [])
            with self.lock:
                self.current_tracks = active_tracks

            # 4. Tripwire & Entry/Exit Counting
            tripwire_delta = self.tripwire.process_tracks(active_tracks)

            # 5. Spatial Zones
            zone_status = self.zones.update_tracks(active_tracks)

            # 6. Activity Classification
            count = len(active_tracks) if len(active_tracks) > 0 else len(detections)
            count_diff = count - self.prev_count
            self.prev_count = count
            
            activity_info = self.activity_classifier.classify(
                count=count,
                tracks=active_tracks,
                count_diff=count_diff,
                entry_rate=float(tripwire_delta["new_entries"]),
                exit_rate=float(tripwire_delta["new_exits"])
            )
            with self.lock:
                self.current_activity = activity_info

            # 7. Alert Rule Evaluation
            if count >= 10:
                self.alert_engine.trigger(
                    alert_type="high_occupancy",
                    severity="high",
                    title="High Occupancy Detected",
                    description=f"Current tracked occupancy ({count}) exceeds threshold (10)."
                )

            # 8. Rendering Overlays
            annotated = self._render_overlays(frame, detections, active_tracks, quality_info, activity_info)
            with self.lock:
                self.latest_raw_frame = frame
                self.latest_annotated_frame = annotated

            # 9. Periodic Database Persistence (every 5 seconds)
            now = time.time()
            if now - self.last_db_save >= 5.0:
                self.db.record_telemetry(
                    camera_id="cam-01-integrated",
                    detected_count=len(detections),
                    active_tracks=len(active_tracks),
                    tripwire_occupancy=self.tripwire.estimated_occupancy,
                    entries=self.tripwire.entries,
                    exits=self.tripwire.exits,
                    activity_class=activity_info["activity"],
                    confidence=activity_info["confidence"],
                    blur_score=quality_info.get("blur_score", 0.0),
                    brightness=quality_info.get("brightness", 0.0),
                    is_reliable=quality_info["reliable"]
                )
                self.last_db_save = now

            # Performance telemetry
            fps_counter += 1
            if now - fps_timer >= 1.0:
                self.pipeline_fps = fps_counter / (now - fps_timer)
                fps_counter = 0
                fps_timer = now
                try:
                    self.cpu_usage_pct = psutil.cpu_percent()
                    self.mem_usage_mb = process.memory_info().rss / (1024 * 1024)
                except Exception:
                    pass

            self.end_to_end_latency_ms = (time.time() - loop_start) * 1000.0
            self.processed_frames += 1
            
            # Maintain smooth processing cadence (~15 FPS display max)
            time.sleep(0.01)

    def _render_overlays(
        self,
        frame: np.ndarray,
        detections: List[Detection],
        tracks: List[Track],
        quality: Dict[str, Any],
        activity: Dict[str, Any]
    ) -> np.ndarray:
        vis = frame.copy()
        h, w = vis.shape[:2]

        # 1. Draw Zones (semi-transparent polygons)
        overlay = vis.copy()
        for zid, zone in self.zones.zones.items():
            pts = zone.polygon.reshape((-1, 1, 2))
            color = (34, 197, 94) if zone.density_percentage < 80 else (239, 68, 68)
            cv2.polylines(overlay, [pts], isClosed=True, color=color, thickness=2)
            # Label
            cv2.putText(overlay, f"{zone.name}: {zone.current_count}/{zone.capacity}",
                        (pts[0][0][0] + 10, pts[0][0][1] + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        cv2.addWeighted(overlay, 0.3, vis, 0.7, 0, vis)

        # 2. Draw Virtual Tripwire Line
        ty = self.tripwire.line_y
        cv2.line(vis, (0, ty), (w, ty), (34, 211, 238), 2)
        cv2.putText(vis, f"TRIPWIRE (Entries: {self.tripwire.entries} | Exits: {self.tripwire.exits})",
                    (15, ty - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (34, 211, 238), 1)

        # 3. Draw Tracked Pedestrians
        for track in tracks:
            x1, y1, x2, y2 = track.bbox
            cv2.rectangle(vis, (x1, y1), (x2, y2), (45, 212, 191), 2)
            
            # Trajectory trail
            if len(track.history) > 1:
                for i in range(1, len(track.history)):
                    cv2.line(vis, track.history[i-1], track.history[i], (34, 211, 238), 2)

            label = f"ID #{track.track_id} ({track.score:.2f})"
            cv2.putText(vis, label, (x1, max(20, y1 - 6)), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (45, 212, 191), 2)

        # 4. Status HUD Banner (Top Left)
        hud_bg = vis[0:65, 0:w].copy()
        vis[0:65, 0:w] = cv2.addWeighted(hud_bg, 0.2, np.zeros_like(hud_bg), 0.8, 0)
        
        info_l1 = f"SENTINEL AI | Model: {self.detector.model_name} | FPS: {self.pipeline_fps:.1f} | Latency: {self.inference_latency_ms:.1f}ms"
        info_l2 = f"Occupancy: {self.tripwire.estimated_occupancy} (Raw: {len(tracks)}) | {activity['activity']} ({activity['confidence']*100:.0f}%) | Quality: {quality.get('status', 'OK')[:25]}"
        
        cv2.putText(vis, info_l1, (15, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.50, (241, 245, 249), 1)
        cv2.putText(vis, info_l2, (15, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.50, (34, 211, 238), 1)

        return vis

    def get_telemetry(self) -> Dict[str, Any]:
        with self.lock:
            return {
                "active": self.running,
                "camera_source": self.stream.source_info,
                "is_synthetic": self.stream.is_synthetic,
                "detector_type": self.detector_type,
                "model_name": self.detector.model_name,
                "fps": round(self.pipeline_fps, 1),
                "inference_latency_ms": round(self.inference_latency_ms, 1),
                "end_to_end_latency_ms": round(self.end_to_end_latency_ms, 1),
                "cpu_percent": round(self.cpu_usage_pct, 1),
                "memory_mb": round(self.mem_usage_mb, 1),
                "raw_detections_count": len(self.current_detections),
                "active_tracks_count": len(self.current_tracks),
                "estimated_occupancy": self.tripwire.estimated_occupancy,
                "entries": self.tripwire.entries,
                "exits": self.tripwire.exits,
                "tripwire_y": self.tripwire.line_y,
                "activity": self.current_activity["activity"],
                "activity_confidence": self.current_activity["confidence"],
                "activity_uncertain": self.current_activity["is_uncertain"],
                "quality_status": self.current_quality.get("status", "Normal"),
                "quality_reliable": self.current_quality.get("reliable", True),
                "blur_score": self.current_quality.get("blur_score", 0.0),
                "brightness": self.current_quality.get("brightness", 0.0),
                "zones": self.zones.get_zone_summary(),
                "recent_alerts": self.alert_engine.get_recent(limit=5)
            }

    def get_annotated_jpeg(self) -> Optional[bytes]:
        with self.lock:
            if self.latest_annotated_frame is not None:
                ret, jpeg = cv2.imencode(".jpg", self.latest_annotated_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
                if ret:
                    return jpeg.tobytes()
        return None
