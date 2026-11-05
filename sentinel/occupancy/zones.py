import cv2
import numpy as np
from typing import List, Dict, Any, Tuple
from sentinel.tracking.tracker import Track

class MonitoringZone:
    """
    Region of Interest (ROI) polygon with capacity monitoring.
    """
    def __init__(self, zone_id: str, name: str, polygon_points: List[Tuple[int, int]], capacity: int = 20):
        self.zone_id = zone_id
        self.name = name
        self.polygon = np.array(polygon_points, dtype=np.int32)
        self.capacity = capacity
        self.current_count = 0
        self.density_percentage = 0.0

    def update_occupancy(self, tracks: List[Track]) -> int:
        count = 0
        for track in tracks:
            cx, cy = track.center
            # cv2.pointPolygonTest returns > 0 if inside, 0 on edge, < 0 if outside
            inside = cv2.pointPolygonTest(self.polygon, (float(cx), float(cy)), False) >= 0
            if inside:
                count += 1
        
        self.current_count = count
        self.density_percentage = round((count / max(1, self.capacity)) * 100.0, 1)
        return self.current_count

    def to_dict(self) -> Dict[str, Any]:
        return {
            "zone_id": self.zone_id,
            "name": self.name,
            "polygon": self.polygon.tolist(),
            "capacity": self.capacity,
            "current_count": self.current_count,
            "density_percentage": self.density_percentage,
            "status": "Normal" if self.density_percentage < 80 else ("High Density" if self.density_percentage < 100 else "Overcapacity")
        }

class ZoneManager:
    """
    Manages multiple spatial zones for a camera.
    """
    def __init__(self, width: int = 640, height: int = 480):
        self.width = width
        self.height = height
        self.zones: Dict[str, MonitoringZone] = {}
        self._init_default_zones()

    def _init_default_zones(self):
        # Default Zone A: Left corridor / entrance area
        p1 = [(0, 0), (int(self.width * 0.45), 0), (int(self.width * 0.45), self.height), (0, self.height)]
        self.zones["zone-a"] = MonitoringZone("zone-a", "Zone A (Corridor)", p1, capacity=10)

        # Default Zone B: Right seating / activity area
        p2 = [(int(self.width * 0.55), 0), (self.width, 0), (self.width, self.height), (int(self.width * 0.55), self.height)]
        self.zones["zone-b"] = MonitoringZone("zone-b", "Zone B (Hall)", p2, capacity=15)

    def update_tracks(self, tracks: List[Track]) -> Dict[str, Any]:
        results = {}
        for zid, zone in self.zones.items():
            zone.update_occupancy(tracks)
            results[zid] = zone.to_dict()
        return results

    def get_zone_summary(self) -> List[Dict[str, Any]]:
        return [z.to_dict() for z in self.zones.values()]
