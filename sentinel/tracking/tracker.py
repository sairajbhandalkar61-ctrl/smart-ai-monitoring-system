import numpy as np
from typing import List, Tuple, Dict, Any
from sentinel.detection.base import Detection

def calculate_iou(boxA: Tuple[int, int, int, int], boxB: Tuple[int, int, int, int]) -> float:
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    interArea = max(0, xB - xA) * max(0, yB - yA)
    boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
    boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])

    denom = float(boxAArea + boxBArea - interArea)
    if denom <= 0:
        return 0.0
    return interArea / denom

class Track:
    """
    State of a temporary, privacy-preserving tracking hypothesis.
    No biometric features or identity attributes are stored.
    """
    _count = 0

    def __init__(self, detection: Detection):
        Track._count += 1
        self.track_id = Track._count
        self.bbox = [detection.x1, detection.y1, detection.x2, detection.y2]
        self.score = detection.score
        self.hits = 1
        self.age = 1
        self.time_since_update = 0
        
        # Trajectory history for velocity and tripwire crossing (limit to last 30 positions)
        cx = (detection.x1 + detection.x2) // 2
        cy = (detection.y1 + detection.y2) // 2
        self.history = [(cx, cy)]
        self.velocity = (0.0, 0.0)

    @property
    def center(self) -> Tuple[int, int]:
        return ((self.bbox[0] + self.bbox[2]) // 2, (self.bbox[1] + self.bbox[3]) // 2)

    def update(self, detection: Detection):
        self.time_since_update = 0
        self.hits += 1
        self.score = detection.score
        
        old_center = self.center
        self.bbox = [detection.x1, detection.y1, detection.x2, detection.y2]
        new_center = self.center
        
        # Simple velocity smoothing
        vx = new_center[0] - old_center[0]
        vy = new_center[1] - old_center[1]
        self.velocity = (0.7 * self.velocity[0] + 0.3 * vx, 0.7 * self.velocity[1] + 0.3 * vy)
        
        self.history.append(new_center)
        if len(self.history) > 30:
            self.history.pop(0)

    def mark_missed(self):
        self.age += 1
        self.time_since_update += 1
        # Extrapolate position with velocity
        self.bbox[0] += int(self.velocity[0])
        self.bbox[1] += int(self.velocity[1])
        self.bbox[2] += int(self.velocity[0])
        self.bbox[3] += int(self.velocity[1])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "track_id": self.track_id,
            "bbox": self.bbox,
            "center": self.center,
            "score": round(self.score, 3),
            "velocity": (round(self.velocity[0], 2), round(self.velocity[1], 2)),
            "age": self.age,
            "hits": self.hits
        }

class RealtimeTracker:
    """
    IoU-based Multi-Object Tracker with trajectory history and velocity extrapolation.
    Fast CPU performance and zero identity retention.
    """
    def __init__(self, max_age: int = 15, min_hits: int = 2, iou_threshold: float = 0.3):
        self.max_age = max_age
        self.min_hits = min_hits
        self.iou_threshold = iou_threshold
        self.tracks: List[Track] = []

    def update(self, detections: List[Detection]) -> List[Track]:
        # 1. Match active tracks against incoming detections via greedy IoU
        matched_tracks = set()
        matched_detections = set()

        if len(self.tracks) > 0 and len(detections) > 0:
            iou_matrix = np.zeros((len(self.tracks), len(detections)), dtype=np.float32)
            for t_idx, track in enumerate(self.tracks):
                for d_idx, det in enumerate(detections):
                    iou_matrix[t_idx, d_idx] = calculate_iou(tuple(track.bbox), det.box_xyxy)

            # Greedy assignment
            while True:
                max_iou = np.max(iou_matrix)
                if max_iou < self.iou_threshold:
                    break
                t_idx, d_idx = np.unravel_index(np.argmax(iou_matrix), iou_matrix.shape)
                if t_idx not in matched_tracks and d_idx not in matched_detections:
                    self.tracks[t_idx].update(detections[d_idx])
                    matched_tracks.add(t_idx)
                    matched_detections.add(d_idx)
                iou_matrix[t_idx, :] = -1.0
                iou_matrix[:, d_idx] = -1.0

        # 2. Mark unmatched tracks
        for t_idx, track in enumerate(self.tracks):
            if t_idx not in matched_tracks:
                track.mark_missed()

        # 3. Create new tracks for unmatched detections
        for d_idx, det in enumerate(detections):
            if d_idx not in matched_detections:
                self.tracks.append(Track(det))

        # 4. Prune expired tracks
        self.tracks = [t for t in self.tracks if t.time_since_update <= self.max_age]

        # 5. Return confirmed active tracks
        return [t for t in self.tracks if t.hits >= self.min_hits or t.age == 1]
