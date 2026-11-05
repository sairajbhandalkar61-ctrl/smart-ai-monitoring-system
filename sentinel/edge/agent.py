import os
import time
import threading
import requests
import psutil
from typing import Optional, Dict, Any, List

from sentinel.pipeline import SentinelPipeline

class SentinelEdgeAgent:
    """
    Dell Edge Agent running on physical Dell Latitude 3420 (Windows 11).
    Ingests local webcam footage, runs CPU-based DL detection & tracking,
    and pushes real-time telemetry securely to the Cloud FastAPI backend.
    """
    def __init__(
        self,
        cloud_api_url: str = "http://127.0.0.1:8000",
        device_id: str = "dell-edge-01",
        device_name: str = "Dell Latitude 3420 Integrated Edge Node",
        token: str = "sentinel_edge_secure_token_2026",
        camera_src: int | str = 0,
        detector_type: str = "ssdlite",
        telemetry_interval: float = 1.0,
        heartbeat_interval: float = 5.0
    ):
        self.cloud_api_url = cloud_api_url.rstrip("/")
        self.device_id = device_id
        self.device_name = device_name
        self.token = token
        self.telemetry_interval = telemetry_interval
        self.heartbeat_interval = heartbeat_interval
        
        # Initialize Edge Vision Pipeline
        self.pipeline = SentinelPipeline(
            camera_src=camera_src,
            detector_type=detector_type,
            frame_width=640,
            frame_height=480,
            adaptive_sampling=True
        )

        self.running = False
        self.lock = threading.Lock()
        self.heartbeat_thread: Optional[threading.Thread] = None
        self.telemetry_thread: Optional[threading.Thread] = None
        
        # Offline buffer queue for resilience
        self.offline_queue: List[Dict[str, Any]] = []
        self.max_queue_size = 500
        self.is_connected = False
        self.process = psutil.Process()

    def start(self):
        with self.lock:
            if self.running:
                return
            print(f"[*] Starting SENTINEL Edge Agent ({self.device_id})...")
            self.pipeline.start()
            self.running = True
            
            # 1. Register with Cloud API
            self._register_with_cloud()

            # 2. Start Background Threads
            self.heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
            self.telemetry_thread = threading.Thread(target=self._telemetry_loop, daemon=True)
            self.heartbeat_thread.start()
            self.telemetry_thread.start()
            print("[+] Edge Agent initialized and pushing live telemetry.")

    def stop(self):
        print("[*] Stopping SENTINEL Edge Agent...")
        self.running = False
        if self.heartbeat_thread and self.heartbeat_thread.is_alive():
            self.heartbeat_thread.join(timeout=1.5)
        if self.telemetry_thread and self.telemetry_thread.is_alive():
            self.telemetry_thread.join(timeout=1.5)
        self.pipeline.stop()
        print("[+] Edge Agent stopped cleanly.")

    def _register_with_cloud(self):
        url = f"{self.cloud_api_url}/api/v1/edge/register"
        payload = {
            "device_id": self.device_id,
            "device_name": self.device_name,
            "token": self.token,
            "camera_source": self.pipeline.stream.source_info
        }
        try:
            r = requests.post(url, json=payload, timeout=5.0)
            if r.status_code == 200:
                print(f"[+] Successfully registered with Cloud at {self.cloud_api_url}")
                self.is_connected = True
            else:
                print(f"[!] Cloud registration returned HTTP {r.status_code}: {r.text}")
        except Exception as e:
            print(f"[!] Unable to connect to Cloud at {url}: {e} (Will buffer offline)")
            self.is_connected = False

    def _heartbeat_loop(self):
        url = f"{self.cloud_api_url}/api/v1/edge/heartbeat"
        while self.running:
            try:
                cpu = psutil.cpu_percent()
                mem = self.process.memory_info().rss / (1024 * 1024)
                payload = {
                    "device_id": self.device_id,
                    "token": self.token,
                    "cpu_percent": round(cpu, 1),
                    "memory_mb": round(mem, 1),
                    "status": "ONLINE" if self.pipeline.running else "STANDBY",
                    "camera_source": self.pipeline.stream.source_info,
                    "active_pipeline": self.pipeline.running
                }
                r = requests.post(url, json=payload, timeout=4.0)
                if r.status_code == 200:
                    self.is_connected = True
                else:
                    self.is_connected = False
            except Exception:
                self.is_connected = False
            
            time.sleep(self.heartbeat_interval)

    def _telemetry_loop(self):
        url = f"{self.cloud_api_url}/api/v1/edge/telemetry"
        while self.running:
            t = self.pipeline.get_telemetry()
            payload = {
                "device_id": self.device_id,
                "camera_id": "cam-01-integrated",
                "timestamp": time.time(),
                "detected_count": t["raw_detections_count"],
                "active_tracks": t["active_tracks_count"],
                "tripwire_occupancy": t["estimated_occupancy"],
                "entries": t["entries"],
                "exits": t["exits"],
                "activity_class": t["activity"],
                "confidence": t["activity_confidence"],
                "blur_score": t["blur_score"],
                "brightness": t["brightness"],
                "is_reliable": t["quality_reliable"],
                "fps": t["fps"],
                "inference_latency_ms": t["inference_latency_ms"],
                "cpu_percent": t["cpu_percent"],
                "memory_mb": t["memory_mb"],
                "zones": t["zones"]
            }

            # Attempt transmission or buffer
            try:
                # Flush offline queue first if any
                if self.offline_queue and self.is_connected:
                    for buffered in self.offline_queue[:10]:
                        requests.post(url, json=buffered, timeout=2.0)
                    self.offline_queue = self.offline_queue[10:]

                r = requests.post(url, json=payload, timeout=2.5)
                if r.status_code == 200:
                    self.is_connected = True
                else:
                    self._buffer_payload(payload)
            except Exception:
                self._buffer_payload(payload)

            time.sleep(self.telemetry_interval)

    def _buffer_payload(self, payload: Dict[str, Any]):
        self.is_connected = False
        if len(self.offline_queue) < self.max_queue_size:
            self.offline_queue.append(payload)

if __name__ == "__main__":
    cloud_url = os.getenv("CLOUD_API_URL", "http://127.0.0.1:8000")
    agent = SentinelEdgeAgent(cloud_api_url=cloud_url)
    try:
        agent.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        agent.stop()
