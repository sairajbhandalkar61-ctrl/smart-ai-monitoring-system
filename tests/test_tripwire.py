import pytest
from sentinel.detection.base import Detection
from sentinel.tracking.tracker import Track
from sentinel.occupancy.tripwire import TripwireLine

def test_tripwire_crossing():
    tw = TripwireLine(y_fraction=0.50, frame_height=400, frame_width=600)
    # line_y is 200
    assert tw.line_y == 200

    # Create track crossing downwards (Entry)
    d_start = Detection(100, 150, 140, 190, score=0.9)
    track = Track(d_start) # center y = 170

    d_cross = Detection(100, 210, 140, 250, score=0.9)
    track.update(d_cross) # center y = 230

    res = tw.process_tracks([track])
    assert res["new_entries"] == 1
    assert tw.entries == 1
    assert tw.estimated_occupancy == 1

def test_tripwire_reconciliation():
    tw = TripwireLine()
    tw.entries = 10
    tw.exits = 2
    assert tw.estimated_occupancy == 8

    # Admin corrects occupancy to 5
    tw.set_manual_occupancy(5)
    assert tw.estimated_occupancy == 5
