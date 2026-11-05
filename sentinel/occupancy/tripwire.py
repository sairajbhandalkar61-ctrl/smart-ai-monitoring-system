from typing import List, Tuple, Dict, Any, Set
from sentinel.tracking.tracker import Track

class TripwireLine:
    """
    Bidirectional virtual tripwire for entry and exit counting.
    Calculates line-segment intersection or vertical threshold crossing.
    """
    def __init__(self, y_fraction: float = 0.50, frame_height: int = 480, frame_width: int = 640):
        self.y_fraction = y_fraction
        self.frame_height = frame_height
        self.frame_width = frame_width
        self.line_y = int(y_fraction * frame_height)
        
        self.entries = 0
        self.exits = 0
        self.initial_occupancy = 0
        self.manual_offset = 0
        
        # Track IDs that have already triggered crossing
        self._crossed_down: Set[int] = set()
        self._crossed_up: Set[int] = set()

    def update_geometry(self, y_fraction: float, frame_height: int, frame_width: int):
        self.y_fraction = y_fraction
        self.frame_height = frame_height
        self.frame_width = frame_width
        self.line_y = int(y_fraction * frame_height)

    def process_tracks(self, tracks: List[Track]) -> Dict[str, int]:
        """
        Evaluates track trajectories against the tripwire line.
        Downwards movement (y increasing) = Entry
        Upwards movement (y decreasing) = Exit
        """
        new_entries = 0
        new_exits = 0

        for track in tracks:
            if len(track.history) < 2:
                continue

            prev_y = track.history[-2][1]
            curr_y = track.history[-1][1]

            # Downward crossing: prev_y < line_y and curr_y >= line_y
            if prev_y < self.line_y and curr_y >= self.line_y:
                if track.track_id not in self._crossed_down:
                    self.entries += 1
                    new_entries += 1
                    self._crossed_down.add(track.track_id)
            
            # Upward crossing: prev_y > line_y and curr_y <= line_y
            elif prev_y > self.line_y and curr_y <= self.line_y:
                if track.track_id not in self._crossed_up:
                    self.exits += 1
                    new_exits += 1
                    self._crossed_up.add(track.track_id)

        # Cleanup memory for dead tracks
        active_ids = {t.track_id for t in tracks}
        self._crossed_down = {tid for tid in self._crossed_down if tid in active_ids}
        self._crossed_up = {tid for tid in self._crossed_up if tid in active_ids}

        return {
            "new_entries": new_entries,
            "new_exits": new_exits
        }

    @property
    def estimated_occupancy(self) -> int:
        occ = self.initial_occupancy + self.entries - self.exits + self.manual_offset
        return max(0, occ)

    def set_manual_occupancy(self, correct_occupancy: int):
        """Allows facility manager to reconcile accumulated tracking drift."""
        current_calc = self.initial_occupancy + self.entries - self.exits
        self.manual_offset = correct_occupancy - current_calc

    def to_dict(self) -> Dict[str, Any]:
        return {
            "line_y": self.line_y,
            "y_fraction": self.y_fraction,
            "entries": self.entries,
            "exits": self.exits,
            "estimated_occupancy": self.estimated_occupancy,
            "manual_offset": self.manual_offset
        }
