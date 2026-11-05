import os
import cv2
import time
import threading
from typing import Optional, Tuple
import numpy as np

class ResilientVideoStream:
    """
    Thread-safe, non-blocking video capture engine.
    Designed for Windows DirectShow and CPU-constrained hardware.
    Drops old frames to prevent capture buffer latency accumulation.
    """
    def __init__(self, src: int | str = 0, backend: str = "DSHOW", width: int = 640, height: int = 480):
        self.src = src
        self.backend_str = backend
        self.width = width
        self.height = height
        
        self.cap: Optional[cv2.VideoCapture] = None
        self.lock = threading.Lock()
        self.running = False
        self.thread: Optional[threading.Thread] = None
        
        self.latest_frame: Optional[np.ndarray] = None
        self.frame_id = 0
        self.last_frame_time = time.time()
        self.measured_fps = 0.0
        self.is_synthetic = False
        self.source_info = "Not connected"

    def _get_cv2_backend(self):
        if isinstance(self.src, int):
            if os.name == 'nt' and self.backend_str.upper() == "DSHOW":
                return cv2.CAP_DSHOW
            elif os.name == 'nt' and self.backend_str.upper() == "MSMF":
                return cv2.CAP_MSMF
        return cv2.CAP_ANY

    def start(self) -> bool:
        with self.lock:
            if self.running:
                return True
            
            backend = self._get_cv2_backend()
            try:
                self.cap = cv2.VideoCapture(self.src, backend)
                if self.cap.isOpened():
                    self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
                    self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
                    self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                    
                    ret, test_frame = self.cap.read()
                    if ret and test_frame is not None:
                        self.latest_frame = test_frame
                        self.is_synthetic = False
                        self.source_info = f"Hardware Camera ({self.src}) [{self.width}x{self.height}]"
                    else:
                        self.cap.release()
                        self.cap = None
            except Exception as e:
                self.cap = None

            if self.cap is None or not self.cap.isOpened():
                # Fallback to synthetic / sample image feed for testing or headless environments
                self.is_synthetic = True
                self.source_info = "Synthetic Stand-in Feed (Camera Unavailable)"
                self.latest_frame = self._generate_synthetic_frame("Camera Initializing...")

            self.running = True
            self.thread = threading.Thread(target=self._capture_loop, daemon=True)
            self.thread.start()
            return True

    def _generate_synthetic_frame(self, text: str) -> np.ndarray:
        frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        frame[:] = (15, 23, 42)  # Dark slate background
        cv2.putText(frame, text, (30, self.height // 2), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (34, 211, 238), 2)
        cv2.putText(frame, f"SENTINEL AI STAND-IN FEED | {time.strftime('%H:%M:%S')}", (30, self.height - 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (148, 163, 184), 1)
        return frame

    def _capture_loop(self):
        fps_counter = 0
        fps_timer = time.time()
        
        while self.running:
            if self.cap is not None and self.cap.isOpened() and not self.is_synthetic:
                ret, frame = self.cap.read()
                if ret and frame is not None:
                    with self.lock:
                        self.latest_frame = frame
                        self.frame_id += 1
                        self.last_frame_time = time.time()
                else:
                    time.sleep(0.02)
            else:
                # Synthetic feed tick at ~15 FPS
                time.sleep(0.066)
                with self.lock:
                    self.latest_frame = self._generate_synthetic_frame("SENTINEL AI - Simulated Feed")
                    self.frame_id += 1
                    self.last_frame_time = time.time()
            
            fps_counter += 1
            now = time.time()
            if now - fps_timer >= 1.0:
                self.measured_fps = fps_counter / (now - fps_timer)
                fps_counter = 0
                fps_timer = now

    def read(self) -> Tuple[bool, Optional[np.ndarray], int]:
        """Returns (success, frame, frame_id). Safe non-blocking clone."""
        with self.lock:
            if self.latest_frame is not None:
                return True, self.latest_frame.copy(), self.frame_id
            return False, None, 0

    def stop(self):
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)
        with self.lock:
            if self.cap is not None:
                self.cap.release()
                self.cap = None
        self.source_info = "Stopped"

    def release(self):
        self.stop()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
