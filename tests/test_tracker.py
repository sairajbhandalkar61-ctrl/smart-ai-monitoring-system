import pytest
from sentinel.detection.base import Detection
from sentinel.tracking.tracker import RealtimeTracker

def test_tracker_creation_and_update():
    tracker = RealtimeTracker(max_age=5, min_hits=1)
    
    # Frame 1: Detection at (100, 100, 150, 200)
    d1 = [Detection(100, 100, 150, 200, score=0.9)]
    tracks1 = tracker.update(d1)
    assert len(tracks1) == 1
    t1_id = tracks1[0].track_id

    # Frame 2: Slightly moved detection (105, 105, 155, 205)
    d2 = [Detection(105, 105, 155, 205, score=0.88)]
    tracks2 = tracker.update(d2)
    assert len(tracks2) == 1
    assert tracks2[0].track_id == t1_id
    assert tracks2[0].hits == 2

def test_tracker_expiration():
    tracker = RealtimeTracker(max_age=2, min_hits=1)
    d1 = [Detection(50, 50, 90, 90, score=0.85)]
    tracker.update(d1)
    assert len(tracker.tracks) == 1

    # Miss 3 frames -> track should expire
    tracker.update([])
    tracker.update([])
    tracker.update([])
    assert len(tracker.tracks) == 0
